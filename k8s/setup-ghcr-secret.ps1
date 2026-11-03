
param(
    [string]$Namespace
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw 'kubectl was not found. Install kubectl and configure a Kubernetes context first.'
}

$context = & kubectl config current-context
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($context)) {
    throw 'No active Kubernetes context. Configure kubectl before creating the GHCR secret.'
}

if ([string]::IsNullOrWhiteSpace($Namespace)) {
    $configuredNamespace = & kubectl config view --minify -o 'jsonpath={.contexts[0].context.namespace}'
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not determine the namespace for the active Kubernetes context.'
    }
    if ($null -eq $configuredNamespace) {
        $Namespace = ''
    }
    else {
        $Namespace = [string]::Join('', $configuredNamespace).Trim()
    }
}

if ([string]::IsNullOrWhiteSpace($Namespace)) {
    $Namespace = 'default'
}

# Corrected Kubernetes namespace validation
if ($Namespace.Length -gt 63 -or $Namespace -notmatch '^[a-z0-9]([-a-z0-9]*[a-z0-9])?$') {
    throw "Invalid Kubernetes namespace '$Namespace'."
}

$null = & kubectl get namespace $Namespace --output name
if ($LASTEXITCODE -ne 0) {
    throw "Kubernetes namespace '$Namespace' does not exist or is not accessible."
}

$secureToken = Read-Host -Prompt 'Paste your classic PAT (input is hidden)' -AsSecureString
$bstr = [IntPtr]::Zero
$token = $null
$dockerConfig = $null
$dockerConfigJson = $null
$manifest = $null

try {
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    $token = $token.Trim()

    if ([string]::IsNullOrWhiteSpace($token)) {
        throw 'The token cannot be empty.'
    }

    if ($token -match '[^\x21-\x7E]') {
        throw 'The token contains whitespace or non-printable characters. Copy only the token value, without quotes or surrounding text, and try again.'
    }

    $headers = @{
        Authorization = "Bearer $token"
        Accept = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
        'User-Agent' = 'employee-api-ghcr-setup'
    }

    try {
        $apiResponse = Invoke-WebRequest `
            -Uri 'https://api.github.com/user' `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop
    }
    catch {
        $httpResponse = $_.Exception.Response
        $statusCode = $null
        $responseBody = $_.Exception.Message

        if ($httpResponse -is [System.Net.HttpWebResponse]) {
            $statusCode = [int]$httpResponse.StatusCode
            $responseStream = $httpResponse.GetResponseStream()

            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $responseBody = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        elseif ($httpResponse -and $httpResponse.GetType().FullName -eq 'System.Net.Http.HttpResponseMessage') {
            $statusCode = [int]$httpResponse.StatusCode
            $responseBody = $httpResponse.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        }

        if ($null -ne $statusCode) {
            throw "GitHub token validation failed (HTTP $statusCode): $responseBody"
        }

        throw "GitHub token validation failed: $responseBody"
    }

    $identity = $apiResponse.Content | ConvertFrom-Json
    $username = $identity.login

    if ([string]::IsNullOrWhiteSpace($username)) {
        throw 'GitHub authenticated the request but did not return an account login.'
    }

    $scopes = @()
    $scopeHeader = $apiResponse.Headers['X-OAuth-Scopes']

    if (-not [string]::IsNullOrWhiteSpace($scopeHeader)) {
        $scopes = $scopeHeader.Split(',') | ForEach-Object { $_.Trim() }
    }

    if ($scopes -notcontains 'read:packages') {
        throw "Authenticated as '$username', but this token does not report the required read:packages scope. Use a classic PAT with read:packages and access to the GHCR package."
    }

    $auth = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes("${username}:$token")
    )

    $dockerConfig = @{
        auths = @{
            'ghcr.io' = @{
                username = $username
                password = $token
                auth = $auth
            }
        }
    }

    $dockerConfigJson = ConvertTo-Json -InputObject $dockerConfig -Depth 4 -Compress

    $encodedConfig = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes($dockerConfigJson)
    )

    $manifest = @"
apiVersion: v1
kind: Secret
metadata:
  name: ghcr-secret
  namespace: $Namespace
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: $encodedConfig
"@

    $manifest | & kubectl apply --namespace $Namespace -f -

    if ($LASTEXITCODE -ne 0) {
        throw "kubectl could not create or update ghcr-secret in namespace '$Namespace'."
    }

    Write-Output "SUCCESS: GitHub authenticated as $username; ghcr-secret is ready in namespace $Namespace."
}
finally {
    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }

    if ($secureToken) {
        $secureToken.Dispose()
    }

    $token = $null
    $headers = $null
    $apiResponse = $null
    $identity = $null
    $auth = $null
    $encodedConfig = $null
    $dockerConfig = $null
    $dockerConfigJson = $null
    $manifest = $null
}
