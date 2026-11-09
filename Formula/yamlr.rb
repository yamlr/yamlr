# typed: false
# frozen_string_literal: true

# Homebrew Formula for Yamlr
# Install via: brew install yamlr/tap/yamlr
class Yamlr < Formula
  desc "Reconcile and repair Kubernetes configurations before deployment"
  homepage "https://yamlr.dev"
  version "0.1.0"
  license :cannot_represent

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-macos-aarch64.tar.gz"
      sha256 "2350162ba219525552a6af37d62d8edad4a1c0e58ad1ff1dfc247a5466a8cba7"
    else
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-macos-x86_64.tar.gz"
      sha256 "bf2b3df18d4b1efd7c35639b93dfcfd09b16f3f3deb217ac2ca76955a72ebc1e"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-linux-aarch64.tar.gz"
      sha256 "b0863c4532b865cc0159648e53df5c62302fba6f513d1549f56ed65da4c2bd56"
    else
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-linux-x86_64.tar.gz"
      sha256 "a601c2b05bb3000161104b095c4728b75a9986fe7c7ef722bad6c7dede90c875"
    end
  end

  def install
    bin.install "yamlr"
  end

  test do
    assert_match "Autonomous Resolution Plane", shell_output("#{bin}/yamlr --help")
  end
end