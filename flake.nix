{
  description = "Automatic git commit message generator using AI models & the OpenRouter API";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      pyproject-nix,
      systems,
      self,
    }:
    let
      project = pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };

      inherit (project.pyproject.project) version;

      forAllSystems =
        f:
        nixpkgs.lib.genAttrs (import systems) (
          system:
          f rec {
            pkgs = import nixpkgs { inherit system; };
            python = pkgs.python312;
          }
        );
    in
    {
      apps = forAllSystems (
        { pkgs, ... }:
        {
          default = self.apps.${pkgs.system}.bump-version;
          bump-version = {
            type = "app";
            program = pkgs.lib.getExe (pkgs.callPackage ./scripts/bump-version.nix { inherit version; });
          };
        }
      );

      devShells = forAllSystems (
        { pkgs, python }:
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.commitizen
              pkgs.uv
              python
            ];
          };
        }
      );

      packages = forAllSystems (
        { pkgs, python, ... }:
        {
          default = self.packages.${pkgs.system}.acmsg;
          acmsg =
            let
              attrs = project.renderers.buildPythonPackage { inherit python; };
            in
            python.pkgs.buildPythonPackage attrs;
        }
      );

      overlays.default = (
        final: prev: {
          acmsg = self.packages.${prev.system}.acmsg;
        }
      );
    };
}
