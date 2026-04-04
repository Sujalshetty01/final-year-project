from fastapi import Request, HTTPException, status

ROLES = ["admin", "user"]

# Example: role-based dependency
async def require_role(request: Request, role: str):
    user_role = request.headers.get("X-Role", "user")
    if user_role != role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
