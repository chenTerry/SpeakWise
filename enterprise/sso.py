"""
SSO Integration - 单点登录集成

提供企业 SSO 功能：
- SSOIntegration: SSO 集成类
- OAuth2Config: OAuth2 配置
- SAMLConfig: SAML 配置

Version: v0.9.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import json
import hashlib
import secrets


class SSOProvider(str, Enum):
    """SSO 提供商"""
    OAUTH2 = "oauth2"
    SAML = "saml"
    LDAP = "ldap"
    OIDC = "oidc"


class SSOStatus(str, Enum):
    """SSO 状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CONFIGURING = "configuring"
    ERROR = "error"


@dataclass
class OAuth2Config:
    """OAuth2 配置"""
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    redirect_uri: str
    scope: str = "openid email profile"
    response_type: str = "code"
    grant_type: str = "authorization_code"
    pkce_enabled: bool = True
    state_ttl_seconds: int = 600
    token_ttl_seconds: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含 secret）"""
        return {
            "client_id": self.client_id,
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
            "userinfo_url": self.userinfo_url,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": self.response_type,
            "grant_type": self.grant_type,
            "pkce_enabled": self.pkce_enabled,
        }


@dataclass
class SAMLConfig:
    """SAML 配置"""
    idp_entity_id: str
    idp_sso_url: str
    idp_certificate: str
    sp_entity_id: str
    sp_acs_url: str
    sp_certificate: str
    sp_private_key: str
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    requested_authn_context: Optional[str] = None
    attribute_mapping: Dict[str, str] = field(default_factory=lambda: {
        "email": "email",
        "name": "name",
        "first_name": "firstName",
        "last_name": "lastName",
    })

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含私钥）"""
        return {
            "idp_entity_id": self.idp_entity_id,
            "idp_sso_url": self.idp_sso_url,
            "sp_entity_id": self.sp_entity_id,
            "sp_acs_url": self.sp_acs_url,
            "name_id_format": self.name_id_format,
            "attribute_mapping": self.attribute_mapping,
        }


@dataclass
class LDAPConfig:
    """LDAP 配置"""
    host: str
    port: int = 389
    use_ssl: bool = False
    base_dn: str = ""
    bind_dn: str = ""
    bind_password: str = ""
    user_search_base: str = ""
    user_filter: str = "(uid={username})"
    attribute_mapping: Dict[str, str] = field(default_factory=lambda: {
        "email": "mail",
        "name": "cn",
        "username": "uid",
    })
    group_search_base: str = ""
    group_filter: str = "(member={dn})"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含密码）"""
        return {
            "host": self.host,
            "port": self.port,
            "use_ssl": self.use_ssl,
            "base_dn": self.base_dn,
            "bind_dn": self.bind_dn,
            "user_search_base": self.user_search_base,
            "user_filter": self.user_filter,
            "attribute_mapping": self.attribute_mapping,
        }


@dataclass
class SSOSession:
    """SSO 会话"""
    id: str
    tenant_id: str
    provider: SSOProvider
    user_id: Optional[str] = None
    email: Optional[str] = None
    state: str = ""
    code_verifier: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """检查会话是否有效"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "provider": self.provider.value,
            "user_id": self.user_id,
            "email": self.email,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }


class SSOIntegration:
    """SSO 集成类"""

    def __init__(self, storage_path: str = "data/sso_config.json"):
        self.storage_path = storage_path
        self._configs: Dict[str, Dict[str, Any]] = {}  # tenant_id -> {provider: config}
        self._sessions: Dict[str, SSOSession] = {}
        self._state_mapping: Dict[str, str] = {}  # state -> session_id
        self._user_callback: Optional[Callable] = None
        self._load()

    def _load(self):
        """加载配置"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._configs = data.get("configs", {})
        except Exception:
            pass

    def _save(self):
        """保存配置"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump({"configs": self._configs}, f, indent=2, ensure_ascii=False)

    def configure_oauth2(
        self,
        tenant_id: str,
        config: OAuth2Config,
    ) -> bool:
        """配置 OAuth2"""
        if tenant_id not in self._configs:
            self._configs[tenant_id] = {}

        self._configs[tenant_id]["oauth2"] = {
            **config.to_dict(),
            "client_secret_hash": hashlib.sha256(config.client_secret.encode()).hexdigest(),
            "enabled": True,
        }
        self._save()
        return True

    def configure_saml(
        self,
        tenant_id: str,
        config: SAMLConfig,
    ) -> bool:
        """配置 SAML"""
        if tenant_id not in self._configs:
            self._configs[tenant_id] = {}

        self._configs[tenant_id]["saml"] = {
            **config.to_dict(),
            "enabled": True,
        }
        self._save()
        return True

    def configure_ldap(
        self,
        tenant_id: str,
        config: LDAPConfig,
    ) -> bool:
        """配置 LDAP"""
        if tenant_id not in self._configs:
            self._configs[tenant_id] = {}

        self._configs[tenant_id]["ldap"] = {
            **config.to_dict(),
            "enabled": True,
        }
        self._save()
        return True

    def get_config(self, tenant_id: str, provider: SSOProvider) -> Optional[Dict[str, Any]]:
        """获取配置"""
        tenant_configs = self._configs.get(tenant_id, {})
        return tenant_configs.get(provider.value)

    def is_enabled(self, tenant_id: str, provider: SSOProvider) -> bool:
        """检查是否启用"""
        config = self.get_config(tenant_id, provider)
        return config is not None and config.get("enabled", False)

    def create_auth_url(
        self,
        tenant_id: str,
        provider: SSOProvider,
        redirect_uri: Optional[str] = None,
    ) -> Optional[str]:
        """创建认证 URL"""
        if provider == SSOProvider.OAUTH2:
            return self._create_oauth2_url(tenant_id, redirect_uri)
        elif provider == SSOProvider.SAML:
            return self._create_saml_request(tenant_id, redirect_uri)
        return None

    def handle_callback(
        self,
        tenant_id: str,
        provider: SSOProvider,
        params: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """处理回调"""
        if provider == SSOProvider.OAUTH2:
            return self._handle_oauth2_callback(tenant_id, params)
        elif provider == SSOProvider.SAML:
            return self._handle_saml_callback(tenant_id, params)
        return None

    def validate_token(
        self,
        tenant_id: str,
        provider: SSOProvider,
        token: str,
    ) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        config = self.get_config(tenant_id, provider)
        if not config:
            return None

        # 简化实现：实际应该调用 provider 的验证 API
        return {
            "valid": True,
            "user_id": f"user_{tenant_id}",
            "email": "user@example.com",
        }

    def create_session(
        self,
        tenant_id: str,
        provider: SSOProvider,
    ) -> SSOSession:
        """创建 SSO 会话"""
        session_id = f"sso_{secrets.token_urlsafe(16)}"
        state = secrets.token_urlsafe(32)

        session = SSOSession(
            id=session_id,
            tenant_id=tenant_id,
            provider=provider,
            state=state,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )

        self._sessions[session_id] = session
        self._state_mapping[state] = session_id

        return session

    def get_session(self, state: str) -> Optional[SSOSession]:
        """获取会话"""
        session_id = self._state_mapping.get(state)
        if session_id:
            return self._sessions.get(session_id)
        return None

    def complete_session(
        self,
        session: SSOSession,
        user_info: Dict[str, Any],
    ) -> bool:
        """完成会话"""
        session.user_id = user_info.get("user_id")
        session.email = user_info.get("email")
        session.metadata["completed_at"] = datetime.utcnow().isoformat()
        return True

    def set_user_callback(self, callback: Callable):
        """设置用户创建/获取回调"""
        self._user_callback = callback

    def _create_oauth2_url(self, tenant_id: str, redirect_uri: Optional[str] = None) -> Optional[str]:
        """创建 OAuth2 认证 URL"""
        config = self.get_config(tenant_id, SSOProvider.OAUTH2)
        if not config:
            return None

        session = self.create_session(tenant_id, SSOProvider.OAUTH2)

        # PKCE
        code_verifier = secrets.token_urlsafe(32)
        session.code_verifier = code_verifier
        self._sessions[session.id] = session

        code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()

        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri or config["redirect_uri"],
            "response_type": config["response_type"],
            "scope": config["scope"],
            "state": session.state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{config['authorization_url']}?{query}"

    def _create_saml_request(self, tenant_id: str, redirect_uri: Optional[str] = None) -> Optional[str]:
        """创建 SAML 请求"""
        config = self.get_config(tenant_id, SSOProvider.SAML)
        if not config:
            return None

        session = self.create_session(tenant_id, SSOProvider.SAML)

        # 简化实现：实际应该生成 SAML AuthnRequest
        return f"{config['idp_sso_url']}?RelayState={session.state}"

    def _handle_oauth2_callback(
        self,
        tenant_id: str,
        params: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """处理 OAuth2 回调"""
        config = self.get_config(tenant_id, SSOProvider.OAUTH2)
        if not config:
            return None

        state = params.get("state")
        code = params.get("code")

        if not state or not code:
            return None

        session = self.get_session(state)
        if not session or not session.is_valid:
            return None

        # 简化实现：实际应该交换 code 获取 token
        user_info = {
            "user_id": f"user_{tenant_id}_{secrets.token_hex(8)}",
            "email": f"user{secrets.token_hex(4)}@example.com",
            "name": "SSO User",
        }

        self.complete_session(session, user_info)

        # 调用用户回调
        if self._user_callback:
            self._user_callback(tenant_id, user_info)

        return user_info

    def _handle_saml_callback(
        self,
        tenant_id: str,
        params: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """处理 SAML 回调"""
        relay_state = params.get("RelayState")

        if not relay_state:
            return None

        session = self.get_session(relay_state)
        if not session or not session.is_valid:
            return None

        # 简化实现：实际应该解析 SAML Response
        user_info = {
            "user_id": f"user_{tenant_id}_{secrets.token_hex(8)}",
            "email": f"user{secrets.token_hex(4)}@example.com",
            "name": "SSO User",
        }

        self.complete_session(session, user_info)

        if self._user_callback:
            self._user_callback(tenant_id, user_info)

        return user_info

    def get_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """获取 SSO 统计"""
        tenant_sessions = [
            s for s in self._sessions.values()
            if s.tenant_id == tenant_id
        ]

        by_provider = {}
        for session in tenant_sessions:
            provider = session.provider.value
            if provider not in by_provider:
                by_provider[provider] = {"total": 0, "completed": 0}
            by_provider[provider]["total"] += 1
            if session.user_id:
                by_provider[provider]["completed"] += 1

        return {
            "total_sessions": len(tenant_sessions),
            "by_provider": by_provider,
            "enabled_providers": [
                provider
                for provider in SSOProvider
                if self.is_enabled(tenant_id, provider)
            ],
        }

    def disable_sso(self, tenant_id: str, provider: SSOProvider) -> bool:
        """禁用 SSO"""
        if tenant_id in self._configs and provider.value in self._configs[tenant_id]:
            self._configs[tenant_id][provider.value]["enabled"] = False
            self._save()
            return True
        return False
