# Kubernetes deployment

## Configure private GHCR image pulls

The API check and a Kubernetes image pull are separate checks. To create or
update the `ghcr-secret` referenced by `deployment.yaml`:

1. Create a **classic** GitHub personal access token with `read:packages`.
   The token's account must also have read access to the package
   `ghcr.io/rk-swetha/employee-api-devops`.
2. From the repository root, run:

   ```powershell
   .\k8s\setup-ghcr-secret.ps1
   ```

   The script checks `GET https://api.github.com/user`, reports HTTP errors,
   verifies the `read:packages` scope, and creates the secret in the active
   kubectl namespace (or `default` if the context has no namespace set). The
   token is entered as a secure prompt and is not written to the manifest or
   printed. To target a specific namespace, pass `-Namespace <name>`.
3. Apply the deployment to that same namespace and check its rollout:

   ```powershell
   kubectl apply -f .\k8s\deployment.yaml
   kubectl rollout status deployment/employee-api
   ```

If the rollout reports `ErrImagePull` or `ImagePullBackOff`, check that the
package exists, the token account has package access, and the secret and
deployment are in the same namespace. The token must not be committed or
shared.
