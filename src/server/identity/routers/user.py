from fastapi import APIRouter, Request, HTTPException

from ..identity_node import IdentityNode
from ..models import UserModel, DataBaseModel, UserUpdate


router = APIRouter(prefix="/user", tags=["user"])


@router.put("/add")
def add_user(model: UserModel, request: Request):
    node: IdentityNode = request.state.node

    try:
        result = node.add_user(
            model.nickname, model.password, model.ip, model.port, model.database_id)
    except:
        raise HTTPException(
            status_code=500, detail="add user failed!")
    else:
        return {"success": result}


@router.post("/password/{nickname}")
def get_pasword(nickname: str, model: DataBaseModel, request: Request):
    node: IdentityNode = request.state.node

    try:
        pasw = node.get_pasword(nickname, model.database_id)
    except:
        raise HTTPException(
            status_code=500, detail="get password failed!")
    else:
        return {"password": pasw}


@router.delete("/delete/{nickname}")
def delete_user(nickname: str, model: DataBaseModel, request: Request):
    node: IdentityNode = request.state.node

    try:
        result = node.delete_user(nickname, model.database_id)
    except:
        raise HTTPException(
            status_code=500, detail="delete user failed!")
    else:
        return {"success": result}


@router.post("/ip_port/{nickname}")
def get_ip_port(nickname: str, model: DataBaseModel, request: Request):
    node: IdentityNode = request.state.node

    try:
        ip_port = node.get_ip_port(nickname, model.database_id)
    except:
        raise HTTPException(
            status_code=500, detail="get ip and port failed!"
        )
    else:
        return {"ip_port": ip_port}


@router.put("/update")
def update_user(model: UserUpdate, request: Request):
    node: IdentityNode = request.state.node

    try:
        user = node.update_user(model.nickname, model.ip,
                                model.port, model.database_id)
    except:
        raise HTTPException(
            status_code=500, detail="update user failed!"
        )
    else:
        return {"success": user}
