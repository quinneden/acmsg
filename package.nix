{ python3, python3Packages, ... }:
python3Packages.buildPythonPackage {
  name = "acmsg";
  format = "pyproject";
  src = ./.;
  propagatedBuildInputs = [
    (python3.withPackages (
      ps: with ps; [
        pytest
        requests
        pyyaml
        poetry-core
      ]
    ))
  ];
}
