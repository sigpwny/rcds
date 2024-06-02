{
  description = "rCDS, but actually functional";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = with pkgs; mkShellNoCC {
          packages = [
            colima
            docker
            self.packages.${system}.rcds
          ];
          # docker-py relies on DOCKER_HOST, which colima doesn't seem to set properly.
          # use this one-liner: ```
          # $ export DOCKER_HOST=$(docker context inspect $(docker context show) | awk -F '"' '/"Host"/ {print $4}')
          # ```
        };
        packages = {
          rcds = with pkgs.python311Packages; buildPythonPackage {
            pname = "rcds";
            version = "0.1.5";
            format = "pyproject";

            src = ./.;

            nativeBuildInputs = [
              pkgs.python311Packages.poetry-core
            ];

            propagatedBuildInputs = with pkgs.python311Packages; [
              jinja2
              click
              docker
              jsonschema
              kubernetes
              pathspec
              pyyaml
              requests
              requests-toolbelt
            ];

            meta = with pkgs.lib; {
              description = "redpwn's challenge deployment system";
              homepage = "https://github.com/redpwn/rcds";
              license = licenses.bsd3;
            };
          };
        };
      });
}
