{
  description = "A basic flake using pyproject.toml project metadata";

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

      forAllSystems =
        f:
        nixpkgs.lib.genAttrs (import systems) (
          system:
          f rec {
            pkgs = nixpkgs.legacyPackages.${system};
            python = pkgs.python312;
          }
        );
    in
    {
      devShells = forAllSystems (
        { pkgs, python }:
        {
          default =
            let
              arg = project.renderers.withPackages { inherit python; };
              pythonEnv = python.withPackages arg;
            in
            pkgs.mkShell { packages = [ pythonEnv ]; };
        }
      );

      packages = forAllSystems (
        { python, ... }:
        rec {
          acmsg =
            let
              attrs = project.renderers.buildPythonPackage { inherit python; };
            in
            python.pkgs.buildPythonPackage attrs;

          default = acmsg;
        }
      );

      overlays.default = (
        final: prev: {
          acmsg = self.packages.${prev.system}.acmsg;
        }
      );
    };
}
