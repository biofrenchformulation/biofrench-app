# GitHub Actions Workflows

## Release Workflow

The `release.yml` workflow automates the process of creating a new release of the BioFrench Android app. This workflow replaces the manual steps previously performed by the `wnt_biofrench_app.bat` script.

### Features

- **On-demand execution**: Manually trigger releases via GitHub Actions UI
- **Automated testing**: Runs unit tests before building the release
- **Automated APK building**: Builds a signed release APK
- **Automatic release creation**: Creates GitHub releases with assets
- **Asset uploads**: Automatically uploads APK and medicines.json

### Prerequisites

**No additional setup required!**

The workflow uses the existing keystore files that are already committed to the repository (`app/keystore/release_new.keystore`). The signing configuration is already set up in `app/build.gradle` with the necessary credentials.

All you need is:
- Push access to the repository (to create tags)
- Workflow execution permissions (default for repository members)

### How to Use

1. **Navigate to Actions tab**
   - Go to your repository on GitHub
   - Click on the **Actions** tab

2. **Select the workflow**
   - Click on **Create Release** in the left sidebar

3. **Run the workflow**
   - Click **Run workflow** button (top right)
   - Fill in the required inputs:
     - **Release version**: e.g., `v1.0.0`, `v1.1.0`
     - **Release notes**: Description of changes in this release
   - Click **Run workflow**

4. **Monitor progress**
   - Watch the workflow execution in real-time
   - Check for any errors in the logs

5. **Verify release**
   - Once completed, go to the **Releases** page
   - Your new release should be listed with:
     - Release version as the title
     - Release notes in the description
     - `biofrench-android-app.apk` attached
     - `medicines.json` attached

### Workflow Steps

The workflow performs the following steps:

1. **Checkout repository**: Fetches the latest code
2. **Set up JDK 11**: Configures Java environment
3. **Run tests**: Executes unit tests (`gradlew testDebugUnitTest`)
4. **Build release APK**: Compiles and signs the APK (`gradlew assembleRelease`)
5. **Verify APK**: Confirms the APK was built successfully
6. **Create git tag**: Tags the current commit with the version
7. **Push tag**: Pushes the tag to GitHub
8. **Create GitHub release**: Creates release with APK and medicines.json

### Troubleshooting

#### Tests fail
- Review test logs in the workflow output
- Fix failing tests before creating a release

#### Tag already exists
- Delete the existing tag if you want to recreate it:
  ```bash
  git tag -d v1.0.0
  git push origin :refs/tags/v1.0.0
  ```

### Comparison with wnt_biofrench_app.bat

| Feature | Batch Script | GitHub Actions Workflow |
|---------|--------------|------------------------|
| Trigger | Manual execution | GitHub UI (on-demand) |
| Environment | Local Windows | GitHub-hosted runner |
| APK signing | Local keystore | Secret-stored keystore |
| Testing | Manual command | Automated |
| Release creation | Manual `gh` CLI | Automated action |
| Asset upload | Manual paths | Automated |
| Accessibility | Local machine only | Anywhere with GitHub access |

### Benefits

- **No local setup required**: Works from any machine with GitHub access
- **Secure credential handling**: Keystore stored as encrypted secret
- **Consistent environment**: Same build environment every time
- **Audit trail**: All releases tracked in GitHub Actions history
- **Collaborative**: Team members can create releases without local setup
