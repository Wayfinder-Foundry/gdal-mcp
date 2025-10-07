#!/bin/bash
set -e

echo "🚀 Setting up GDAL MCP development environment..."

# Ensure we're in the workspace directory
cd /workspace

# Install dependencies with uv
echo "📦 Installing Python dependencies..."
uv sync --all-extras

# Verify installation
echo "✅ Verifying installation..."
uv run gdal --help || echo "⚠️  CLI not available yet (expected during first build)"

# Run quality checks to ensure everything is set up correctly
echo "🔍 Running initial quality checks..."
uv run ruff check . || echo "⚠️  Ruff check found issues (run 'uv run ruff check . --fix' to auto-fix)"
uv run mypy src/ || echo "⚠️  MyPy found type issues"

# Run tests to verify everything works
echo "🧪 Running tests..."
uv run pytest test/ -v || echo "⚠️  Some tests failed"

# Create sample data directory if it doesn't exist
echo "📁 Setting up test data directories..."
mkdir -p /workspace/test/data
mkdir -p /workspace/.cache
mkdir -p /workspace/.uv

# Display helpful information
echo ""
echo "✨ Development environment ready!"
echo ""
echo "📚 Quick Start Commands:"
echo "  uv run gdal --help                    # Show CLI help"
echo "  uv run pytest test/ -v                # Run all tests"
echo "  uv run ruff check . --fix             # Fix linting issues"
echo "  uv run mypy src/                      # Type check"
echo "  uv run gdal --transport stdio         # Run MCP server (stdio)"
echo "  uv run gdal --transport http --port 8000  # Run HTTP server"
echo ""
echo "🔍 Verification:"
echo "  bash .devcontainer/verify-setup.sh    # Verify environment setup"
echo ""
echo "📖 Documentation:"
echo "  README.md         - Project overview"
echo "  CONTRIBUTING.md   - Development guide"
echo "  QUICKSTART.md     - Usage guide"
echo "  docs/             - Design documents and ADRs"
echo ""
echo "🎉 Happy coding!"
