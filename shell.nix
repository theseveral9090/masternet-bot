{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python3.withPackages (ps: with ps; [
      python-telegram-bot
      aiohttp
      aiohttp-socks
      pysocks
      requests
    ]))
  ];
}
