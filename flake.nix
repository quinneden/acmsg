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
      devShells = forAllSystems (
        { pkgs, python }:
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.uv
              python
            ];
          };
        }
      );

      packages = forAllSystems (
        { pkgs, python, ... }:
        rec {
          default = acmsg;
          acmsg =
            let
              attrs = project.renderers.buildPythonPackage { inherit python; };
            in
            python.pkgs.buildPythonPackage attrs;

          bump-version = pkgs.callPackage ./scripts/bump-version.nix { inherit version; };
        }
      );

      overlays.default = (
        final: prev: {
          acmsg = self.packages.${prev.system}.acmsg;
        }
      );
    };
}
