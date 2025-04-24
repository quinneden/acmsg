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
      ...
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
            python = pkgs.python313;
          }
        );
    in
    {
      inherit project;
      devShells = forAllSystems (
        { pkgs, python }:
        {
          default =
            let
              deps = project.renderers.withPackages { inherit python; };
              pythonEnv = python.withPackages deps;
            in
            pkgs.mkShell {
              packages = [
                pkgs.uv
                python
                pythonEnv
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

          create-release = pkgs.callPackage ./scripts/create-release { inherit version; };
        }
      );

      overlays.default = (
        final: prev: {
          acmsg = self.packages.${prev.system}.acmsg;
        }
      );
    };
}
