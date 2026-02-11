param(
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [string]$Branch = 'main'
)
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
  git init
  git add -A
  git commit -m "chore(review): initial commit for review" -q 2>$null || Write-Output "commit skipped"
}
if (-not (git remote)) {
  git remote add origin $RemoteUrl
} else {
  git remote set-url origin $RemoteUrl
}
git fetch origin 2>$null || Write-Output "fetch skipped"
git push -u origin $Branch 2>$null || Write-Output "push branch skipped"
git push origin v1.0-first-review --force
Write-Output "Pushed tag v1.0-first-review to $RemoteUrl"
