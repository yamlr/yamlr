class Yamlr < Formula
  desc "The Kubernetes Safety Engine (v0.1.0 Alpha)"
  homepage "https://yamlr.dev"
  url "https://github.com/yamlr/yamlr/releases/download/v0.1.0/yamlr-macos-amd64.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # TODO: Update with real hash
  # Yamlr is proprietary software; see the repository LICENSE for terms.
  license :cannot_represent

  def install
    bin.install "yamlr"
    # Install man pages
    man1.install Dir["docs/man/man1/*.1"]
  end

  test do
    system "#{bin}/yamlr", "welcome"
  end
end
