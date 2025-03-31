{
  description = "A command-line tool for generating git commit messages using AI and the OpenRouter API.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    { nixpkgs, self, ... }:
    let
      forEachSystem =
        f:
        nixpkgs.lib.genAttrs [ "aarch64-darwin" "aarch64-linux" ] (
          system:
          f {
            pkgs = import nixpkgs {
              inherit system;
              overlays = [ self.overlays.default ];
            };
          }
        );
    in
    {
      packages = forEachSystem (
        { pkgs }:
        {
          inherit (pkgs) acmsg;
        }
      );

      overlays.default = final: prev: {
        acmsg = prev.callPackage ./package.nix { };
      };
    };
}
