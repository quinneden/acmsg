{
  bash,
  writeShellApplication,
  version,
}:
writeShellApplication {
  name = "acmsg-create-release";
  runtimeInputs = [ bash ];

  text = ''
    version=${version}; export version
    bash ${./create-release.sh}
  '';
}
