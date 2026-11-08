# typed: false
# frozen_string_literal: true

# Homebrew Formula for Yamlr
# Install via: brew install yamlr/tap/yamlr
class Yamlr < Formula
  desc "Reconcile and repair Kubernetes configurations before deployment"
  homepage "https://yamlr.dev"
  version "0.1.0"
  # Yamlr is proprietary software; see the repository LICENSE for terms.
  license :cannot_represent

  on_macos do
    if Hardware::CPU.arm?
      url "https://get.yamlr.dev/v#{version}/yamlr-macos-aarch64.tar.gz"
      sha256 "3a448021a262bbfd581a45064b527edd9768c5142c96d03a38bf0ace3bcf21a7"
    else
      url "https://get.yamlr.dev/v#{version}/yamlr-macos-x86_64.tar.gz"
      sha256 "13a4058e2424354bb6d5090edaf56cc7697000036addb761064fb59abb8047ec"
    end
  end

  on_linux do
    if Hardware::CPU.intel?
      url "https://get.yamlr.dev/v#{version}/yamlr-linux-x86_64.tar.gz"
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
