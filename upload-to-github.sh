#!/bin/bash

# Upload to GitHub Script
# This script helps set up and upload the DNS Update Service to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="dns-update"
GITHUB_USER="floyd68"
GITHUB_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if git is installed
check_git() {
    if ! command -v git > /dev/null 2>&1; then
        print_error "Git is not installed. Please install git first."
        exit 1
    fi
}

# Function to check if we're in a git repository
check_git_repo() {
    if [ ! -d ".git" ]; then
        print_status "Initializing git repository..."
        git init
    fi
}

# Function to create initial commit
create_initial_commit() {
    print_status "Creating initial commit..."
    
    # Add all files
    git add .
    
    # Create initial commit
    git commit -m "Initial commit: DNS Update Service

- Flask-based web service for Route53 DNS A record updates
- Plain text API for simple IP address updates
- AWS Route53 integration with boto3
- Systemd service installation and management
- Nginx reverse proxy with SSL support
- Docker containerization
- Comprehensive documentation and examples"
}

# Function to create GitHub repository
create_github_repo() {
    print_header "Creating GitHub Repository"
    echo "================================"
    
    print_status "Repository will be created at: $GITHUB_URL"
    echo ""
    echo "Please ensure you have:"
    echo "1. GitHub account: $GITHUB_USER"
    echo "2. GitHub CLI installed (gh) or manual repository creation"
    echo "3. Proper authentication set up"
    echo ""
    
    read -p "Do you want to create the repository using GitHub CLI? (y/N): " use_gh
    
    if [[ $use_gh =~ ^[Yy]$ ]]; then
        if command -v gh > /dev/null 2>&1; then
            print_status "Creating repository with GitHub CLI..."
            gh repo create "$GITHUB_USER/$REPO_NAME" \
                --public \
                --description "Flask-based web service for updating Route53 DNS A records via HTTP POST" \
                --homepage "https://github.com/$GITHUB_USER/$REPO_NAME" \
                --source . \
                --remote origin \
                --push
            print_status "Repository created and pushed to GitHub!"
        else
            print_error "GitHub CLI (gh) is not installed."
            print_warning "Please install GitHub CLI or create the repository manually."
            manual_repo_creation
        fi
    else
        manual_repo_creation
    fi
}

# Function for manual repository creation
manual_repo_creation() {
    print_header "Manual Repository Creation"
    echo "=============================="
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: Flask-based web service for updating Route53 DNS A records via HTTP POST"
    echo "4. Make it Public"
    echo "5. Do NOT initialize with README (we already have one)"
    echo "6. Click 'Create repository'"
    echo ""
    echo "After creating the repository, run:"
    echo "  git remote add origin $GITHUB_URL"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
    
    read -p "Press Enter when you've created the repository..."
    
    # Add remote and push
    print_status "Adding remote origin..."
    git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"
    
    print_status "Setting main branch..."
    git branch -M main
    
    print_status "Pushing to GitHub..."
    git push -u origin main
}

# Function to set up repository features
setup_repository_features() {
    print_header "Setting up Repository Features"
    echo "==================================="
    echo ""
    echo "The repository includes:"
    echo "✅ Issue templates (bug reports, feature requests)"
    echo "✅ Pull request template"
    echo "✅ Contributing guidelines"
    echo "✅ MIT License"
    echo "✅ GitHub Actions CI/CD workflow"
    echo "✅ Comprehensive README"
    echo "✅ Docker support"
    echo "✅ Systemd service scripts"
    echo "✅ Nginx reverse proxy configuration"
    echo ""
    echo "Next steps:"
    echo "1. Review the repository on GitHub"
    echo "2. Set up branch protection rules (recommended)"
    echo "3. Configure GitHub Actions secrets if needed"
    echo "4. Add topics/tags to the repository"
    echo ""
}

# Function to show final instructions
show_final_instructions() {
    print_header "Upload Complete!"
    echo "=================="
    echo ""
    echo -e "${GREEN}Your DNS Update Service has been successfully uploaded to GitHub!${NC}"
    echo ""
    echo "Repository URL: $GITHUB_URL"
    echo ""
    echo "What's included:"
    echo "📁 Complete Flask application"
    echo "📁 Systemd service installation scripts"
    echo "📁 Nginx reverse proxy configuration"
    echo "📁 Docker containerization"
    echo "📁 Comprehensive documentation"
    echo "📁 GitHub Actions CI/CD workflow"
    echo "📁 Issue and PR templates"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository: $GITHUB_URL"
    echo "2. Review and customize the README if needed"
    echo "3. Set up branch protection rules"
    echo "4. Configure any additional GitHub features"
    echo "5. Share your repository with others!"
    echo ""
    echo -e "${YELLOW}Happy coding! 🚀${NC}"
}

# Main function
main() {
    print_header "DNS Update Service - GitHub Upload"
    echo "========================================"
    echo ""
    
    # Check prerequisites
    check_git
    check_git_repo
    
    # Create initial commit
    create_initial_commit
    
    # Create GitHub repository
    create_github_repo
    
    # Setup repository features
    setup_repository_features
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main 