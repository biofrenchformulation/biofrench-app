# Release Guide

This document explains how to create a new release of the BioFrench Android app using the automated GitHub Actions workflow.

## Quick Start

1. Go to the [Actions tab](../../actions) in your GitHub repository
2. Click on **Create Release** workflow
3. Click **Run workflow**
4. Fill in:
   - **Release version**: e.g., `v1.0.0`, `v1.1.0`, `v2.0.0`
   - **Release notes**: Description of what's new in this release
5. Click **Run workflow** button
6. Wait for the workflow to complete (typically 5-10 minutes)
7. Check the [Releases page](../../releases) for your new release

## What Happens During a Release?

The automated workflow performs the following steps:

1. **Runs Tests** - Executes all unit tests to ensure code quality
2. **Builds Release APK** - Compiles and signs the production APK
3. **Creates Git Tag** - Tags the current commit with your version
4. **Creates GitHub Release** - Publishes the release with:
   - Release notes you provided
   - Signed APK file (`biofrench-android-app.apk`)
   - Medicine catalog data (`medicines.json`)

## Version Naming Convention

Follow semantic versioning with a `v` prefix:

- **Major version** (v2.0.0): Breaking changes or major feature additions
- **Minor version** (v1.1.0): New features, backward compatible
- **Patch version** (v1.0.1): Bug fixes only

Examples:
- `v1.0.0` - First production release
- `v1.1.0` - Added new medicine categories
- `v1.1.1` - Fixed catalog search bug
- `v2.0.0` - New admin interface redesign

## Release Notes Best Practices

Your release notes should include:

### Good Example
```
Added new medicine categories for cardiovascular drugs.
Fixed issue where search was case-sensitive.
Updated medicine database with 50 new entries.
Improved performance of catalog loading by 30%.
```

### What to Include
- ✅ New features added
- ✅ Bugs fixed
- ✅ Performance improvements
- ✅ Database/content updates
- ✅ Breaking changes (if any)

### What to Avoid
- ❌ Technical implementation details
- ❌ Internal refactoring that doesn't affect users
- ❌ Commit hashes or pull request numbers

## Troubleshooting

### Workflow fails during tests
- Check the test logs in the workflow output
- Fix failing tests locally first
- Push fixes and run the workflow again

### Workflow fails during build
- Ensure all code compiles locally with `./gradlew assembleRelease`
- Check for missing dependencies
- Verify keystore files are present in `app/keystore/`

### Tag already exists
If you need to recreate a release with the same version:

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Delete the GitHub release from the Releases page
# Then run the workflow again
```

## Manual Release (Alternative)

If you prefer or need to create releases manually, you can still use the `wnt_biofrench_app.bat` script on Windows:

```batch
wnt_biofrench_app.bat create_release
```

However, the GitHub Actions workflow is recommended for:
- ✅ Consistency across all releases
- ✅ No local environment setup needed
- ✅ Better security (no credentials on local machine)
- ✅ Audit trail and logs
- ✅ Team collaboration

## Additional Resources

- [GitHub Actions Workflow Documentation](.github/workflows/README.md)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Developer Guide](DEVELOPER_GUIDE.md)

## Need Help?

If you encounter issues not covered in this guide:
1. Check the workflow logs in the Actions tab
2. Review the [troubleshooting section](#troubleshooting)
3. Contact the development team
4. Open an issue in the repository
