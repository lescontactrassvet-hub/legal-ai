# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary
from fastapi import APIRouter
router = APIRouter()
@router.get("/me")
def me_stub(): return {"detail": "stub"}
