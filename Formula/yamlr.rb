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
      sha256 "8ba56df5e06fb6093406a23611de4e92e7e2042ae11d76acce12deb13c1ac86c"
    else
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-macos-x86_64.tar.gz"
      sha256 "d1b494e3a12eada33cb1cc387f81edbb8fd026a5db418e430b3d78f1651c028a"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-linux-aarch64.tar.gz"
      sha256 "194ab6af807d289c3b2692b1a19fbe15e9a71e4bdc1e0fab2631a195bd3ed72f"
    else
      url "https://github.com/yamlr/yamlr/releases/download/v#{version}/yamlr-linux-x86_64.tar.gz"
      sha256 "2f5df6b3dd50531dc98845299c2c93326664bfdfcfc944e46c2b349e3a44541b"
    end
  end

  def install
    bin.install "yamlr"
  end

  test do
    assert_match "Autonomous Resolution Plane", shell_output("#{bin}/yamlr --help")
  end
end