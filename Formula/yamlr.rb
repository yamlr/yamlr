# typed: false
# frozen_string_literal: true

# Homebrew Formula for Yamlr
# Install via: brew install yamlr/tap/yamlr
class Yamlr < Formula
  desc "Reconcile and repair Kubernetes configurations before deployment"
  homepage "https://yamlr.dev"
  version "0.1.4"
  license :cannot_represent

  on_macos do
    if Hardware::CPU.arm?
      url "https://get.yamlr.dev/v#{version}/yamlr-macos-aarch64.tar.gz"
      sha256 "87ca04e32984959e7d7d4b3c4cb31251dc4141e212fe03970c3ed830f8fadfd9"
    else
      url "https://get.yamlr.dev/v#{version}/yamlr-macos-x86_64.tar.gz"
      sha256 "0b681ba25388768aa64cc2f2279428dcea2e926f819d8c4dbbb9849dc8a513f7"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://get.yamlr.dev/v#{version}/yamlr-linux-aarch64.tar.gz"
      sha256 "4e7d456da2c0581a75c76e34cbf931a4bd7a46f64ed0c9074a00d06f16c36bcd"
    else
      url "https://get.yamlr.dev/v#{version}/yamlr-linux-x86_64.tar.gz"
      sha256 "3557eae8906bd47671683dc97d0c12f0c195f843ab21778ecbd6f4c3604fde13"
    end
  end

  def install
    bin.install "yamlr"
  end

  test do
    assert_match "Configuration Resolution Plane", shell_output("#{bin}/yamlr --help")
  end
end
