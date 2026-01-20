# Sprint 02: API Mobile Nativa

## 🎯 OBJETIVO
Desenvolver APIs nativas específicas para dispositivos móveis com otimizações para conexões limitadas, offline-first e push notifications, garantindo experiência fluida em aplicações mobile.

## 🔧 ESPECIFICAÇÕES TÉCNICAS

### Arquitetura Mobile-First
```
┌─────────────────────────────────────────────────────────┐
│                   API MOBILE NATIVA                      │
├─────────────────────────────────────────────────────────┤
│  Mobile Gateway                                          │
│  ├── Request Optimizer                                   │
│  ├── Data Compression                                    │
│  ├── Batch Operations                                    │
│  └── Offline Sync Manager                               │
├─────────────────────────────────────────────────────────┤
│  Backend Services                                        │
│  ├── Mobile-Optimized Endpoints                         │
│  ├── Push Notification Service                          │
│  ├── Background Sync Service                            │
│  ├── Conflict Resolution                                 │
│  └── Mobile Analytics                                    │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                              │
│  ├── Optimized Queries                                  │
│  ├── Mobile Caching (Redis)                             │
│  ├── Sync Queue (PostgreSQL)                            │
│  └── Offline Storage Support                            │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### 1. Mobile Gateway
```python
# core/mobile/gateway.py
from typing import List, Dict, Optional, Union
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
import gzip
import json
import asyncio

class MobileGateway:
    """Gateway otimizado para requisições mobile."""

    def __init__(self):
        self.compression_threshold = 1024  # 1KB
        self.batch_timeout = 200  # 200ms
        self.max_batch_size = 10

    async def process_request(
        self,
        request: Request,
        user_agent: str
    ) -> Dict:
        """
        Processa requisição mobile com otimizações.

        Args:
            request: Requisição HTTP
            user_agent: User agent do dispositivo

        Returns:
            Resposta otimizada para mobile
        """
        device_info = self._parse_device_info(user_agent)
        
        # Ajustar estratégia baseado no dispositivo
        if device_info["connection_type"] == "slow":
            return await self._process_low_bandwidth(request)
        elif device_info["battery_level"] == "low":
            return await self._process_battery_saving(request)
        else:
            return await self._process_standard(request)

    async def _process_low_bandwidth(self, request: Request) -> Dict:
        """Processamento otimizado para conexões lentas."""
        # Compressão agressiva
        # Redução de dados não essenciais
        # Priorização de conteúdo crítico
        pass

    async def compress_response(self, data: Dict) -> bytes:
        """Comprime resposta se necessário."""
        json_data = json.dumps(data)
        
        if len(json_data) > self.compression_threshold:
            return gzip.compress(json_data.encode())
        
        return json_data.encode()

    def _parse_device_info(self, user_agent: str) -> Dict:
        """Extrai informações do dispositivo do user agent."""
        return {
            "device_type": "mobile",
            "os": "android" if "Android" in user_agent else "ios",
            "connection_type": "fast",  # Detectar via Network Information API
            "battery_level": "normal"   # Detectar via Battery API
        }
```

#### 2. Endpoints Mobile-Optimized
```python
# api/v1/mobile/endpoints.py
from fastapi import APIRouter, Depends, Query, Body
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/mobile/v1", tags=["mobile"])

@router.post("/sync")
async def mobile_sync(
    sync_request: MobileSyncRequest,
    user: User = Depends(get_current_active_user)
):
    """
    Sincronização otimizada para mobile.
    
    Combina múltiplas operações em uma única requisição.
    """
    
    results = {
        "timestamp": datetime.utcnow(),
        "user_id": user.id,
        "operations": []
    }
    
    # Processar operações em batch
    for operation in sync_request.operations:
        try:
            result = await process_sync_operation(operation, user.id)
            results["operations"].append({
                "id": operation.id,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results["operations"].append({
                "id": operation.id,
                "status": "error",
                "error": str(e)
            })
    
    return MobileSyncResponse(**results)

@router.get("/dashboard/lightweight")
async def get_mobile_dashboard(
    user: User = Depends(get_current_active_user),
    include_charts: bool = Query(False),
    data_range: int = Query(7, ge=1, le=30)
):
    """
    Dashboard otimizado para mobile com dados reduzidos.
    """
    
    dashboard_data = {
        "summary": await get_dashboard_summary(user.id, data_range),
        "recent_activities": await get_recent_activities(user.id, limit=5),
        "quick_actions": get_mobile_quick_actions(user)
    }
    
    # Incluir gráficos apenas se solicitado
    if include_charts:
        dashboard_data["charts"] = await get_lightweight_charts(user.id)
    
    return MobileDashboardResponse(**dashboard_data)

@router.post("/batch")
async def batch_operations(
    batch_request: BatchRequest,
    user: User = Depends(get_current_active_user)
):
    """
    Executa múltiplas operações em uma única requisição.
    """
    
    results = []
    
    # Executar operações em paralelo quando possível
    tasks = []
    for operation in batch_request.operations:
        if operation.can_parallelize:
            tasks.append(execute_operation(operation, user.id))
        else:
            # Executar sequencialmente
            result = await execute_operation(operation, user.id)
            results.append(result)
    
    # Aguardar operações paralelas
    if tasks:
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(parallel_results)
    
    return BatchResponse(results=results)

@router.get("/offline-data")
async def get_offline_data(
    user: User = Depends(get_current_active_user),
    modules: List[str] = Query([])
):
    """
    Retorna dados essenciais para funcionamento offline.
    """
    
    offline_data = {
        "user_profile": await get_user_profile(user.id),
        "essential_data": {},
        "last_sync": datetime.utcnow(),
        "sync_token": generate_sync_token(user.id)
    }
    
    # Incluir dados específicos dos módulos solicitados
    for module in modules:
        module_data = await get_module_offline_data(module, user.id)
        offline_data["essential_data"][module] = module_data
    
    return OfflineDataResponse(**offline_data)
```

#### 3. Push Notification Service
```python
# services/mobile/push_notifications.py
from firebase_admin import messaging, credentials
import httpx
from typing import Dict, List, Optional

class PushNotificationService:
    """Serviço de push notifications para mobile."""

    def __init__(self):
        # Inicializar Firebase Admin
        cred = credentials.Certificate("firebase-credentials.json")
        firebase_admin.initialize_app(cred)
        
        self.apns_client = httpx.AsyncClient()  # Para iOS
        self.fcm_client = messaging  # Para Android

    async def send_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        priority: str = "normal"
    ):
        """
        Envia push notification para usuário.

        Args:
            user_id: ID do usuário
            title: Título da notificação
            body: Corpo da notificação
            data: Dados adicionais
            priority: Prioridade (normal, high)
        """
        
        # Buscar tokens do usuário
        user_tokens = await get_user_device_tokens(user_id)
        
        if not user_tokens:
            return {"status": "no_tokens", "sent": 0}

        messages = []
        for token_info in user_tokens:
            if token_info["platform"] == "android":
                message = self._create_fcm_message(
                    token_info["token"], title, body, data, priority
                )
            elif token_info["platform"] == "ios":
                message = self._create_apns_message(
                    token_info["token"], title, body, data, priority
                )
            
            messages.append(message)

        # Enviar em batch
        response = await messaging.send_all(messages)
        
        # Processar resultado
        success_count = response.success_count
        failure_count = response.failure_count
        
        # Remover tokens inválidos
        await self._handle_invalid_tokens(response.responses, user_tokens)
        
        return {
            "status": "sent",
            "success": success_count,
            "failed": failure_count,
            "total": len(messages)
        }

    def _create_fcm_message(
        self, token: str, title: str, body: str, data: Dict, priority: str
    ) -> messaging.Message:
        """Cria mensagem FCM para Android."""
        
        android_config = messaging.AndroidConfig(
            priority=priority,
            notification=messaging.AndroidNotification(
                title=title,
                body=body,
                icon="ic_notification",
                color="#FF6B35"
            )
        )
        
        return messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            android=android_config
        )

    def _create_apns_message(
        self, token: str, title: str, body: str, data: Dict, priority: str
    ) -> messaging.Message:
        """Cria mensagem APNS para iOS."""
        
        apns_config = messaging.APNSConfig(
            headers={"apns-priority": "10" if priority == "high" else "5"},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(title=title, body=body),
                    badge=1,
                    sound="default"
                )
            )
        )
        
        return messaging.Message(
            token=token,
            data=data or {},
            apns=apns_config
        )

    async def _handle_invalid_tokens(self, responses, user_tokens):
        """Remove tokens inválidos do banco."""
        invalid_tokens = []
        
        for i, response in enumerate(responses):
            if not response.success:
                error_code = response.exception.code if response.exception else None
                if error_code in ["invalid-registration-token", "registration-token-not-registered"]:
                    invalid_tokens.append(user_tokens[i]["token"])
        
        if invalid_tokens:
            await remove_invalid_device_tokens(invalid_tokens)
```

#### 4. Offline Sync Manager
```python
# services/mobile/offline_sync.py
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib

class OfflineSyncManager:
    """Gerencia sincronização offline-online."""

    def __init__(self):
        self.conflict_resolvers = {
            "last_write_wins": self._resolve_last_write_wins,
            "user_decides": self._resolve_user_decides,
            "merge": self._resolve_merge
        }

    async def sync_user_data(
        self,
        user_id: int,
        offline_changes: List[Dict],
        last_sync_token: str
    ) -> Dict:
        """
        Sincroniza mudanças offline com o servidor.

        Args:
            user_id: ID do usuário
            offline_changes: Lista de mudanças feitas offline
            last_sync_token: Token da última sincronização

        Returns:
            Resultado da sincronização com conflitos resolvidos
        """
        
        sync_result = {
            "timestamp": datetime.utcnow(),
            "conflicts": [],
            "applied_changes": [],
            "server_changes": [],
            "new_sync_token": self._generate_sync_token(user_id)
        }

        # 1. Obter mudanças do servidor desde last_sync
        server_changes = await self._get_server_changes(user_id, last_sync_token)
        
        # 2. Detectar conflitos
        conflicts = self._detect_conflicts(offline_changes, server_changes)
        
        # 3. Aplicar mudanças sem conflito
        for change in offline_changes:
            if not self._has_conflict(change, conflicts):
                try:
                    await self._apply_change(change, user_id)
                    sync_result["applied_changes"].append(change)
                except Exception as e:
                    change["error"] = str(e)
                    sync_result["conflicts"].append(change)

        # 4. Resolver conflitos
        for conflict in conflicts:
            resolution = await self._resolve_conflict(conflict)
            if resolution["status"] == "resolved":
                sync_result["applied_changes"].append(resolution["change"])
            else:
                sync_result["conflicts"].append(conflict)

        # 5. Retornar mudanças do servidor
        sync_result["server_changes"] = server_changes

        return sync_result

    async def _get_server_changes(
        self, user_id: int, last_sync_token: str
    ) -> List[Dict]:
        """Busca mudanças no servidor desde a última sync."""
        
        # Decodificar token para obter timestamp
        last_sync_time = self._decode_sync_token(last_sync_token)
        
        # Buscar mudanças em todas as tabelas relevantes
        changes = []
        
        tables = ["leads", "customers", "orders", "products", "tasks"]
        
        for table in tables:
            table_changes = await self._get_table_changes(
                table, user_id, last_sync_time
            )
            changes.extend(table_changes)
        
        return changes

    def _detect_conflicts(
        self, offline_changes: List[Dict], server_changes: List[Dict]
    ) -> List[Dict]:
        """Detecta conflitos entre mudanças offline e server."""
        
        conflicts = []
        
        # Criar índice das mudanças do servidor
        server_index = {
            f"{change['table']}:{change['record_id']}": change
            for change in server_changes
        }
        
        for offline_change in offline_changes:
            key = f"{offline_change['table']}:{offline_change['record_id']}"
            
            if key in server_index:
                server_change = server_index[key]
                
                # Verificar se são mudanças conflitantes
                if self._changes_conflict(offline_change, server_change):
                    conflicts.append({
                        "offline_change": offline_change,
                        "server_change": server_change,
                        "type": "data_conflict"
                    })
        
        return conflicts

    def _changes_conflict(self, offline: Dict, server: Dict) -> bool:
        """Verifica se duas mudanças conflitam."""
        
        # Se ambas modificaram os mesmos campos
        offline_fields = set(offline.get("changed_fields", []))
        server_fields = set(server.get("changed_fields", []))
        
        return bool(offline_fields.intersection(server_fields))

    async def _resolve_conflict(self, conflict: Dict) -> Dict:
        """Resolve conflito baseado na estratégia configurada."""
        
        strategy = conflict.get("resolution_strategy", "last_write_wins")
        resolver = self.conflict_resolvers.get(strategy)
        
        if not resolver:
            return {"status": "unresolved", "error": "Unknown strategy"}
        
        return await resolver(conflict)

    async def _resolve_last_write_wins(self, conflict: Dict) -> Dict:
        """Resolve conflito usando last-write-wins."""
        
        offline_change = conflict["offline_change"]
        server_change = conflict["server_change"]
        
        # Comparar timestamps
        if offline_change["timestamp"] > server_change["timestamp"]:
            winning_change = offline_change
        else:
            winning_change = server_change
        
        await self._apply_change(winning_change, conflict["user_id"])
        
        return {
            "status": "resolved",
            "strategy": "last_write_wins",
            "change": winning_change
        }

    async def _resolve_merge(self, conflict: Dict) -> Dict:
        """Resolve conflito fazendo merge dos dados."""
        
        offline_change = conflict["offline_change"]
        server_change = conflict["server_change"]
        
        # Fazer merge dos campos não conflitantes
        merged_data = {**server_change["data"]}
        
        for field, value in offline_change["data"].items():
            if field not in server_change.get("changed_fields", []):
                merged_data[field] = value
        
        merged_change = {
            **offline_change,
            "data": merged_data,
            "strategy": "merge"
        }
        
        await self._apply_change(merged_change, conflict["user_id"])
        
        return {
            "status": "resolved",
            "strategy": "merge",
            "change": merged_change
        }

    def _generate_sync_token(self, user_id: int) -> str:
        """Gera token de sincronização."""
        timestamp = datetime.utcnow().timestamp()
        data = f"{user_id}:{timestamp}"
        token = hashlib.md5(data.encode()).hexdigest()
        return f"{int(timestamp)}:{token}"

    def _decode_sync_token(self, token: str) -> datetime:
        """Decodifica token de sincronização."""
        try:
            timestamp_str = token.split(":")[0]
            timestamp = float(timestamp_str)
            return datetime.fromtimestamp(timestamp)
        except (ValueError, IndexError):
            return datetime.min
```

### Frontend Mobile SDK

#### 1. Mobile SDK Core
```typescript
// mobile-sdk/core/MobileClient.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';

interface MobileClientConfig {
  apiUrl: string;
  authToken: string;
  enableOfflineSync: boolean;
  syncInterval: number;
}

export class MobileClient {
  private config: MobileClientConfig;
  private syncQueue: SyncQueue;
  private offlineStorage: OfflineStorage;
  private isOnline: boolean = true;

  constructor(config: MobileClientConfig) {
    this.config = config;
    this.syncQueue = new SyncQueue();
    this.offlineStorage = new OfflineStorage();
    
    this.initializeNetworkListener();
    this.initializeAutoSync();
  }

  private initializeNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;
      
      if (wasOffline && this.isOnline) {
        // Voltou online - iniciar sync
        this.syncWithServer();
      }
    });
  }

  private initializeAutoSync() {
    if (this.config.enableOfflineSync) {
      setInterval(() => {
        if (this.isOnline) {
          this.syncWithServer();
        }
      }, this.config.syncInterval);
    }
  }

  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    if (!this.isOnline && options.requiresOnline) {
      throw new Error('Operation requires internet connection');
    }

    if (!this.isOnline) {
      // Adicionar à fila de sync
      await this.syncQueue.add({
        endpoint,
        method: options.method || 'GET',
        data: options.data,
        timestamp: new Date()
      });
      
      // Retornar dados do cache se disponível
      return await this.offlineStorage.get(endpoint);
    }

    try {
      const response = await this.makeRequest(endpoint, options);
      
      // Cache response para uso offline
      if (options.cacheable !== false) {
        await this.offlineStorage.set(endpoint, response);
      }
      
      return response;
    } catch (error) {
      // Se falhou, tentar usar cache
      if (options.fallbackToCache !== false) {
        const cachedData = await this.offlineStorage.get(endpoint);
        if (cachedData) {
          return cachedData;
        }
      }
      
      throw error;
    }
  }

  async syncWithServer(): Promise<SyncResult> {
    if (!this.isOnline) {
      return { status: 'offline', synced: 0, conflicts: 0 };
    }

    const pendingOperations = await this.syncQueue.getAll();
    const lastSyncToken = await AsyncStorage.getItem('lastSyncToken');

    try {
      const response = await this.makeRequest('/mobile/v1/sync', {
        method: 'POST',
        data: {
          operations: pendingOperations,
          lastSyncToken
        }
      });

      // Processar resultado da sync
      await this.processSyncResult(response);
      
      // Limpar operações sincronizadas
      await this.syncQueue.clear();
      
      // Salvar novo token
      await AsyncStorage.setItem('lastSyncToken', response.syncToken);

      return {
        status: 'success',
        synced: response.operations.length,
        conflicts: response.conflicts.length
      };
    } catch (error) {
      console.error('Sync failed:', error);
      return { status: 'error', synced: 0, conflicts: 0 };
    }
  }

  private async processSyncResult(result: any) {
    // Aplicar mudanças do servidor
    for (const serverChange of result.serverChanges) {
      await this.offlineStorage.applyServerChange(serverChange);
    }

    // Processar conflitos
    for (const conflict of result.conflicts) {
      await this.handleConflict(conflict);
    }
  }

  private async handleConflict(conflict: any) {
    // Implementar lógica de resolução de conflitos
    // Pode mostrar UI para usuário decidir
    console.warn('Conflict detected:', conflict);
  }
}
```

#### 2. Offline Storage
```typescript
// mobile-sdk/storage/OfflineStorage.ts
import SQLite from 'react-native-sqlite-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

export class OfflineStorage {
  private db: SQLite.SQLiteDatabase;

  async initialize() {
    this.db = await SQLite.openDatabase({
      name: 'conecta_pro_offline.db',
      location: 'default'
    });

    await this.createTables();
  }

  private async createTables() {
    const tables = [
      `
      CREATE TABLE IF NOT EXISTS cached_responses (
        endpoint TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        expires_at INTEGER
      )
      `,
      `
      CREATE TABLE IF NOT EXISTS pending_operations (
        id TEXT PRIMARY KEY,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        data TEXT,
        timestamp INTEGER NOT NULL,
        retry_count INTEGER DEFAULT 0
      )
      `,
      `
      CREATE TABLE IF NOT EXISTS offline_data (
        table_name TEXT NOT NULL,
        record_id TEXT NOT NULL,
        data TEXT NOT NULL,
        version INTEGER NOT NULL,
        last_modified INTEGER NOT NULL,
        is_deleted INTEGER DEFAULT 0,
        PRIMARY KEY (table_name, record_id)
      )
      `
    ];

    for (const sql of tables) {
      await this.db.executeSql(sql);
    }
  }

  async get(endpoint: string): Promise<any> {
    try {
      const [results] = await this.db.executeSql(
        'SELECT data, expires_at FROM cached_responses WHERE endpoint = ?',
        [endpoint]
      );

      if (results.rows.length === 0) {
        return null;
      }

      const row = results.rows.item(0);
      const now = Date.now();

      if (row.expires_at && row.expires_at < now) {
        // Cache expirado
        await this.delete(endpoint);
        return null;
      }

      return JSON.parse(row.data);
    } catch (error) {
      console.error('Error getting cached data:', error);
      return null;
    }
  }

  async set(
    endpoint: string,
    data: any,
    ttl?: number
  ): Promise<void> {
    try {
      const timestamp = Date.now();
      const expiresAt = ttl ? timestamp + ttl : null;

      await this.db.executeSql(
        `
        INSERT OR REPLACE INTO cached_responses 
        (endpoint, data, timestamp, expires_at) 
        VALUES (?, ?, ?, ?)
        `,
        [endpoint, JSON.stringify(data), timestamp, expiresAt]
      );
    } catch (error) {
      console.error('Error caching data:', error);
    }
  }

  async saveOfflineData(
    tableName: string,
    recordId: string,
    data: any
  ): Promise<void> {
    try {
      await this.db.executeSql(
        `
        INSERT OR REPLACE INTO offline_data 
        (table_name, record_id, data, version, last_modified) 
        VALUES (?, ?, ?, ?, ?)
        `,
        [
          tableName,
          recordId,
          JSON.stringify(data),
          data.version || 1,
          Date.now()
        ]
      );
    } catch (error) {
      console.error('Error saving offline data:', error);
    }
  }

  async getOfflineData(
    tableName: string,
    recordId?: string
  ): Promise<any> {
    try {
      let sql = 'SELECT * FROM offline_data WHERE table_name = ? AND is_deleted = 0';
      let params = [tableName];

      if (recordId) {
        sql += ' AND record_id = ?';
        params.push(recordId);
      }

      const [results] = await this.db.executeSql(sql, params);
      
      if (recordId) {
        return results.rows.length > 0 
          ? JSON.parse(results.rows.item(0).data)
          : null;
      }

      const items = [];
      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        items.push({
          ...JSON.parse(row.data),
          _recordId: row.record_id,
          _version: row.version,
          _lastModified: row.last_modified
        });
      }

      return items;
    } catch (error) {
      console.error('Error getting offline data:', error);
      return recordId ? null : [];
    }
  }

  async applyServerChange(change: any): Promise<void> {
    if (change.operation === 'delete') {
      await this.markAsDeleted(change.tableName, change.recordId);
    } else {
      await this.saveOfflineData(
        change.tableName,
        change.recordId,
        change.data
      );
    }
  }

  private async markAsDeleted(
    tableName: string,
    recordId: string
  ): Promise<void> {
    await this.db.executeSql(
      'UPDATE offline_data SET is_deleted = 1 WHERE table_name = ? AND record_id = ?',
      [tableName, recordId]
    );
  }
}
```

## 🗃️ ESTRUTURAS DE DADOS

### 1. Request/Response Models
```python
# schemas/mobile/sync.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MobileSyncOperation(BaseModel):
    """Operação de sincronização mobile."""
    id: str = Field(..., description="ID único da operação")
    table: str = Field(..., description="Tabela afetada")
    operation: str = Field(..., description="Tipo: create, update, delete")
    record_id: str = Field(..., description="ID do registro")
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    can_parallelize: bool = Field(default=True)

class MobileSyncRequest(BaseModel):
    """Request de sincronização."""
    operations: List[MobileSyncOperation]
    last_sync_token: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

class MobileSyncResponse(BaseModel):
    """Response de sincronização."""
    timestamp: datetime
    user_id: int
    operations: List[Dict[str, Any]]
    server_changes: List[Dict[str, Any]] = []
    conflicts: List[Dict[str, Any]] = []
    new_sync_token: str

class MobileDashboardResponse(BaseModel):
    """Dashboard otimizado para mobile."""
    summary: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    quick_actions: List[Dict[str, str]]
    charts: Optional[Dict[str, Any]] = None

class BatchRequest(BaseModel):
    """Request para operações em batch."""
    operations: List[MobileSyncOperation]

class BatchResponse(BaseModel):
    """Response de operações em batch."""
    results: List[Dict[str, Any]]
    execution_time: float
    success_count: int
    error_count: int

class OfflineDataResponse(BaseModel):
    """Dados para funcionamento offline."""
    user_profile: Dict[str, Any]
    essential_data: Dict[str, Any]
    last_sync: datetime
    sync_token: str
    cache_expires_at: datetime
```

### 2. Device Token Model
```python
# models/mobile/device.py
class DeviceToken(Base):
    """Tokens de dispositivos para push notifications."""
    __tablename__ = "device_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), nullable=False, unique=True)
    platform = Column(String(20), nullable=False)  # ios, android
    app_version = Column(String(50))
    os_version = Column(String(50))
    device_model = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="device_tokens")

class PushNotification(Base):
    """Log de notificações enviadas."""
    __tablename__ = "push_notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data_payload = Column(JSON)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    status = Column(String(20), default="sent")  # sent, delivered, read, failed

    # Relacionamentos
    user = relationship("User")
```

## 🚀 IMPLEMENTAÇÃO

### Fase 1: Gateway Mobile (Sprint 1-2)
1. **Mobile Gateway Setup**
   - Request optimization
   - Compression middleware
   - Device detection
   - Batch operations

2. **Core APIs**
   - Mobile-optimized endpoints
   - Lightweight responses
   - Error handling
   - Rate limiting ajustado

### Fase 2: Push Notifications (Sprint 3)
1. **Push Service**
   - Firebase integration
   - iOS/Android support
   - Token management
   - Delivery tracking

2. **Notification Types**
   - System alerts
   - Business events
   - Marketing messages
   - Personal reminders

### Fase 3: Offline Sync (Sprint 4-5)
1. **Sync Engine**
   - Conflict resolution
   - Data versioning
   - Queue management
   - Recovery mechanisms

2. **Client SDK**
   - React Native library
   - Offline storage
   - Auto-sync
   - Conflict UI

### Fase 4: Optimizations (Sprint 6)
1. **Performance**
   - Query optimization
   - Caching strategies
   - Compression
   - CDN integration

2. **Analytics**
   - Mobile metrics
   - Performance monitoring
   - User behavior
   - Error tracking

## 📊 MÉTRICAS E MONITORAMENTO

### Mobile Performance Metrics
```python
# monitoring/mobile_metrics.py
class MobileMetrics:
    """Métricas específicas para mobile."""

    def __init__(self):
        self.metrics = {
            "response_times": [],
            "data_usage": [],
            "offline_usage": [],
            "sync_conflicts": [],
            "push_delivery_rate": 0.0
        }

    async def track_api_call(
        self,
        endpoint: str,
        response_time: float,
        data_size: int,
        user_agent: str
    ):
        """Rastreia chamada de API mobile."""
        
        device_info = self.parse_device_info(user_agent)
        
        await self.record_metric("mobile_api_call", {
            "endpoint": endpoint,
            "response_time": response_time,
            "data_size": data_size,
            "device_type": device_info["device_type"],
            "os": device_info["os"],
            "app_version": device_info["app_version"],
            "timestamp": datetime.utcnow()
        })

    async def track_push_notification(
        self,
        notification_id: str,
        status: str,
        platform: str
    ):
        """Rastreia entrega de push notification."""
        
        await self.record_metric("push_notification", {
            "notification_id": notification_id,
            "status": status,
            "platform": platform,
            "timestamp": datetime.utcnow()
        })

    async def track_sync_operation(
        self,
        user_id: int,
        operations_count: int,
        conflicts_count: int,
        duration: float
    ):
        """Rastreia operação de sincronização."""
        
        await self.record_metric("mobile_sync", {
            "user_id": user_id,
            "operations_count": operations_count,
            "conflicts_count": conflicts_count,
            "duration": duration,
            "timestamp": datetime.utcnow()
        })

    def parse_device_info(self, user_agent: str) -> Dict:
        """Extrai informações do dispositivo."""
        # Implementar parsing do user agent
        return {
            "device_type": "mobile",
            "os": "unknown",
            "app_version": "unknown"
        }
```

### KPIs Específicos
- **Performance:** Response time < 1s, Data usage < 50KB/request
- **Reliability:** 99.9% uptime, < 0.1% sync conflicts
- **Adoption:** 80% mobile users, 95% push enabled
- **Efficiency:** 90% offline capability, < 5s sync time

## 🔒 SEGURANÇA MOBILE

### Mobile Security Best Practices
```python
# security/mobile_security.py
class MobileSecurityManager:
    """Gerencia segurança específica para mobile."""

    def __init__(self):
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,  # Mais permissivo para mobile
            burst_limit=10
        )

    async def validate_mobile_request(
        self,
        request: Request,
        device_token: Optional[str] = None
    ) -> bool:
        """Valida requisição mobile."""
        
        # 1. Verificar rate limiting
        if not await self.rate_limiter.check(request.client.host):
            raise HTTPException(429, "Rate limit exceeded")
        
        # 2. Validar device token se fornecido
        if device_token and not await self.validate_device_token(device_token):
            raise HTTPException(401, "Invalid device token")
        
        # 3. Verificar user agent
        user_agent = request.headers.get("user-agent", "")
        if not self.is_valid_mobile_agent(user_agent):
            raise HTTPException(400, "Invalid user agent")
        
        return True

    async def validate_device_token(self, token: str) -> bool:
        """Valida token do dispositivo."""
        device = await get_device_by_token(token)
        return device and device.is_active

    def is_valid_mobile_agent(self, user_agent: str) -> bool:
        """Verifica se é user agent mobile válido."""
        mobile_patterns = [
            "ConectaPRO-Android",
            "ConectaPRO-iOS",
            "ConectaPRO-Mobile"
        ]
        
        return any(pattern in user_agent for pattern in mobile_patterns)

    async def encrypt_offline_data(self, data: Dict) -> str:
        """Criptografa dados para armazenamento offline."""
        # Implementar criptografia AES-256
        pass

    async def decrypt_offline_data(self, encrypted_data: str) -> Dict:
        """Descriptografa dados do armazenamento offline."""
        # Implementar descriptografia AES-256
        pass
```

## 📋 CHECKLIST DE ENTREGA

### ✅ Backend
- [ ] Mobile Gateway implementado
- [ ] Endpoints otimizados para mobile
- [ ] Push notification service
- [ ] Offline sync manager
- [ ] Conflict resolution
- [ ] Mobile security
- [ ] Compression middleware
- [ ] Batch operations
- [ ] Mobile analytics

### ✅ Client SDK
- [ ] React Native SDK
- [ ] Offline storage (SQLite)
- [ ] Auto-sync functionality
- [ ] Push notifications
- [ ] Network state handling
- [ ] Conflict resolution UI
- [ ] Performance monitoring
- [ ] Error handling
- [ ] TypeScript support

### ✅ DevOps
- [ ] Firebase setup
- [ ] APNs configuration
- [ ] Mobile CI/CD
- [ ] Performance monitoring
- [ ] Crash reporting
- [ ] Mobile analytics
- [ ] A/B testing setup

### ✅ Documentação
- [ ] SDK documentation
- [ ] Integration guide
- [ ] API reference
- [ ] Best practices
- [ ] Troubleshooting
- [ ] Performance guide

## 🎯 CRITÉRIOS DE SUCESSO

### Performance Metrics
- Response time < 1 segundo
- Data transfer < 50KB por request
- Sync time < 5 segundos
- Offline capability > 90%

### User Experience
- App store rating > 4.5
- Crash rate < 0.1%
- ANR rate < 0.01%
- Battery usage optimization

### Business Impact
- 80% dos usuários usando mobile
- 40% aumento no engagement
- 25% redução em tickets de suporte
- 95% push notification opt-in

---

**📅 Duração Estimada:** 6 sprints (12 semanas)
**👥 Equipe Necessária:** 2 desenvolvedores mobile + 2 backend + 1 DevOps
**💰 Investimento:** R$ 150.000 - R$ 200.000
**🚀 Impacto Esperado:** Experiência mobile nativa de alta performance com capacidades offline completas
