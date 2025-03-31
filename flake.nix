{
  description = "A command-line tool for generating git commit messages using AI and the OpenRouter API.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      forEachSystem =
        f:
        nixpkgs.lib.genAttrs [ "aarch64-darwin" "aarch64-linux" ] (
          system: f { pkgs = import nixpkgs { inherit system; }; }
        );
    in
    {
      packages = forEachSystem (
        { pkgs }:
        {
          default = pkgs.callPackage ./package.nix { };
        }
      );
    };
}
