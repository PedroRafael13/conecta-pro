# SKILL: MOBILE APPS
## ERP Conecta Mais - Fase 2

**Versao:** 1.0
**Modulo:** Mobile
**Sprints:** 31-34 (Q4 2026)
**Executor:** Claude Opus 4.5

---

## INDICE

1. [Visao Geral](#1-visao-geral)
2. [Arquitetura Mobile](#2-arquitetura-mobile)
3. [App Colaborador](#3-app-colaborador)
4. [App Gestor](#4-app-gestor)
5. [App Cliente](#5-app-cliente)
6. [App Tecnico](#6-app-tecnico)
7. [App Vendedor](#7-app-vendedor)
8. [Componentes Compartilhados](#8-componentes-compartilhados)
9. [Offline First](#9-offline-first)
10. [Push Notifications](#10-push-notifications)
11. [Biometria e Seguranca](#11-biometria-e-seguranca)
12. [Testes Mobile](#12-testes-mobile)

---

## 1. VISAO GERAL

### 1.1 Ecossistema de Apps

```
APPS MOBILE (React Native)
==========================

1. APP COLABORADOR
   - Ponto biometrico
   - Visualizacao de escala
   - Solicitacoes (ferias, folgas)
   - Holerite digital
   - Comunicados

2. APP GESTOR
   - Dashboard operacional
   - Aprovacoes
   - Gestao de equipe
   - Alertas criticos
   - Relatorios

3. APP CLIENTE
   - Portal do cliente
   - Faturas e boletos
   - Abertura de chamados
   - Avaliacao de servicos
   - Documentos

4. APP TECNICO
   - Ordens de servico
   - Checklist digital
   - Fotos e evidencias
   - Navegacao GPS
   - Assinatura digital

5. APP VENDEDOR
   - CRM mobile
   - Propostas comerciais
   - Catalogo de servicos
   - Agenda de visitas
   - Metas e comissoes
```

### 1.2 Stack Tecnologico

```typescript
// Stack Mobile
const MOBILE_STACK = {
  framework: "React Native 0.75+",
  linguagem: "TypeScript 5.5+",
  stateManagement: "Zustand",
  navigation: "React Navigation 7",
  storage: "WatermelonDB (offline)",
  sync: "Sync Engine Custom",
  push: "Firebase Cloud Messaging",
  biometria: "react-native-biometrics",
  camera: "react-native-vision-camera",
  maps: "react-native-maps",
  charts: "Victory Native",
  forms: "React Hook Form + Zod",
  http: "Axios + React Query",
  ci_cd: "Fastlane + EAS Build",
};
```

---

## 2. ARQUITETURA MOBILE

### 2.1 Estrutura de Projeto

```
mobile/
├── apps/
│   ├── colaborador/
│   │   ├── src/
│   │   │   ├── screens/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── navigation/
│   │   ├── app.json
│   │   └── package.json
│   ├── gestor/
│   ├── cliente/
│   ├── tecnico/
│   └── vendedor/
├── packages/
│   ├── shared-ui/           # Componentes compartilhados
│   ├── shared-hooks/        # Hooks reutilizaveis
│   ├── shared-stores/       # Stores Zustand
│   ├── sync-engine/         # Motor de sincronizacao
│   ├── biometric-auth/      # Autenticacao biometrica
│   └── push-notifications/  # Notificacoes push
├── turbo.json               # Monorepo Turborepo
└── package.json
```

### 2.2 Configuracao Monorepo

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".expo/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### 2.3 API Client

```typescript
// packages/shared-hooks/src/api/client.ts
"""
Cliente API para comunicacao com backend.

Implementa interceptors, refresh token e retry logic.
"""

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getStoredToken, refreshToken, clearAuth } from '../auth/storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://api.conectamais.com.br';

/**
 * Cria instancia configurada do Axios.
 *
 * @returns Instancia Axios configurada
 */
export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - adiciona token
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const token = await getStoredToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => Promise.reject(error)
  );

  // Response interceptor - refresh token
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && originalRequest) {
        try {
          const newToken = await refreshToken();
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return client(originalRequest);
          }
        } catch {
          await clearAuth();
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();
```

---

## 3. APP COLABORADOR

### 3.1 Funcionalidades

```
APP COLABORADOR
===============

1. PONTO BIOMETRICO
   - Registro via facial/digital
   - Geolocalizacao obrigatoria
   - Foto selfie automatica
   - Validacao anti-fraude
   - Historico de registros

2. ESCALA DE TRABALHO
   - Calendario mensal
   - Trocas de turno
   - Solicitacao de folga
   - Banco de horas

3. SOLICITACOES
   - Ferias
   - Atestados
   - Adiantamentos
   - Justificativas

4. DOCUMENTOS
   - Holerite digital
   - Informe de rendimentos
   - Contratos
   - Comunicados

5. PERFIL
   - Dados pessoais
   - Configuracoes
   - Notificacoes
```

### 3.2 Tela de Ponto

```typescript
// apps/colaborador/src/screens/PontoScreen.tsx
"""
Tela de registro de ponto biometrico.

Implementa captura facial, geolocalizacao e validacao.
"""

import React, { useState, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { Camera, useCameraDevice, PhotoFile } from 'react-native-vision-camera';
import * as Location from 'expo-location';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import { Button, Card, Avatar } from '@shared-ui';
import { useBiometricAuth } from '@biometric-auth';
import { useAuthStore } from '../stores/authStore';
import { pontoService } from '../services/pontoService';

interface PontoData {
  tipo: 'entrada' | 'saida' | 'intervalo_inicio' | 'intervalo_fim';
  latitude: number;
  longitude: number;
  foto_base64: string;
  device_info: string;
}

export function PontoScreen(): React.ReactElement {
  const [loading, setLoading] = useState(false);
  const [tipoRegistro, setTipoRegistro] = useState<PontoData['tipo'] | null>(null);
  const cameraRef = useRef<Camera>(null);
  const device = useCameraDevice('front');

  const { user } = useAuthStore();
  const { authenticate } = useBiometricAuth();
  const queryClient = useQueryClient();

  const registrarPontoMutation = useMutation({
    mutationFn: pontoService.registrar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ponto-hoje'] });
      Alert.alert('Sucesso', 'Ponto registrado com sucesso!');
    },
    onError: (error: Error) => {
      Alert.alert('Erro', error.message);
    },
  });

  /**
   * Captura foto para validacao.
   *
   * @returns Foto em base64
   */
  const capturarFoto = useCallback(async (): Promise<string> => {
    if (!cameraRef.current) {
      throw new Error('Camera nao disponivel');
    }

    const photo: PhotoFile = await cameraRef.current.takePhoto({
      qualityPrioritization: 'speed',
      flash: 'off',
    });

    // Converter para base64
    const base64 = await convertToBase64(photo.path);
    return base64;
  }, []);

  /**
   * Obtem localizacao atual.
   *
   * @returns Coordenadas GPS
   */
  const obterLocalizacao = useCallback(async (): Promise<{
    latitude: number;
    longitude: number;
  }> => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      throw new Error('Permissao de localizacao negada');
    }

    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.High,
    });

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
    };
  }, []);

  /**
   * Registra ponto com validacoes.
   *
   * @param tipo - Tipo de registro
   */
  const registrarPonto = useCallback(async (tipo: PontoData['tipo']) => {
    setLoading(true);
    setTipoRegistro(tipo);

    try {
      // 1. Autenticacao biometrica
      const bioAuth = await authenticate('Confirme sua identidade');
      if (!bioAuth.success) {
        throw new Error('Autenticacao biometrica falhou');
      }

      // 2. Capturar foto
      const foto = await capturarFoto();

      // 3. Obter localizacao
      const coords = await obterLocalizacao();

      // 4. Montar payload
      const pontoData: PontoData = {
        tipo,
        latitude: coords.latitude,
        longitude: coords.longitude,
        foto_base64: foto,
        device_info: await getDeviceInfo(),
      };

      // 5. Enviar registro
      await registrarPontoMutation.mutateAsync(pontoData);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro desconhecido';
      Alert.alert('Erro', message);
    } finally {
      setLoading(false);
      setTipoRegistro(null);
    }
  }, [authenticate, capturarFoto, obterLocalizacao, registrarPontoMutation]);

  if (!device) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Camera nao disponivel</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Avatar source={{ uri: user?.foto_url }} size={60} />
        <View style={styles.headerInfo}>
          <Text style={styles.userName}>{user?.nome}</Text>
          <Text style={styles.dateText}>
            {format(new Date(), "EEEE, dd 'de' MMMM", { locale: ptBR })}
          </Text>
        </View>
      </View>

      {/* Camera Preview */}
      <View style={styles.cameraContainer}>
        <Camera
          ref={cameraRef}
          style={styles.camera}
          device={device}
          isActive={true}
          photo={true}
        />
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#fff" />
            <Text style={styles.loadingText}>
              Registrando {tipoRegistro?.replace('_', ' ')}...
            </Text>
          </View>
        )}
      </View>

      {/* Botoes de Registro */}
      <View style={styles.buttonsContainer}>
        <View style={styles.buttonRow}>
          <Button
            title="Entrada"
            icon="login"
            variant="primary"
            size="large"
            disabled={loading}
            onPress={() => registrarPonto('entrada')}
            style={styles.button}
          />
          <Button
            title="Saida"
            icon="logout"
            variant="secondary"
            size="large"
            disabled={loading}
            onPress={() => registrarPonto('saida')}
            style={styles.button}
          />
        </View>
        <View style={styles.buttonRow}>
          <Button
            title="Intervalo"
            icon="coffee"
            variant="outline"
            size="medium"
            disabled={loading}
            onPress={() => registrarPonto('intervalo_inicio')}
            style={styles.buttonSmall}
          />
          <Button
            title="Retorno"
            icon="arrow-back"
            variant="outline"
            size="medium"
            disabled={loading}
            onPress={() => registrarPonto('intervalo_fim')}
            style={styles.buttonSmall}
          />
        </View>
      </View>

      {/* Registros do Dia */}
      <RegistrosDia />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  headerInfo: {
    marginLeft: 12,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  dateText: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  cameraContainer: {
    height: 300,
    margin: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  camera: {
    flex: 1,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 12,
    fontSize: 16,
  },
  buttonsContainer: {
    padding: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  button: {
    flex: 1,
    marginHorizontal: 6,
  },
  buttonSmall: {
    flex: 1,
    marginHorizontal: 6,
  },
  errorText: {
    fontSize: 16,
    color: '#d32f2f',
    textAlign: 'center',
    marginTop: 50,
  },
});
```

### 3.3 Store de Autenticacao

```typescript
// apps/colaborador/src/stores/authStore.ts
"""
Store Zustand para autenticacao.

Gerencia estado de usuario e tokens.
"""

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  id: string;
  nome: string;
  email: string;
  foto_url: string | null;
  cargo: string;
  setor: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User) => void;
  setTokens: (token: string, refreshToken: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user: User) =>
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
        }),

      setTokens: (token: string, refreshToken: string) =>
        set({
          token,
          refreshToken,
        }),

      logout: () =>
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      setLoading: (isLoading: boolean) =>
        set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

---

## 4. APP GESTOR

### 4.1 Funcionalidades

```
APP GESTOR
==========

1. DASHBOARD
   - KPIs em tempo real
   - Alertas criticos
   - Ocupacao de postos
   - Indicadores financeiros

2. APROVACOES
   - Solicitacoes pendentes
   - Workflow de aprovacao
   - Historico

3. EQUIPE
   - Presenca hoje
   - Escalas
   - Performance
   - Ocorrencias

4. OPERACAO
   - Mapa de postos
   - Status de contratos
   - Eventos criticos

5. RELATORIOS
   - Geracao sob demanda
   - Compartilhamento
   - Exportacao
```

### 4.2 Dashboard Screen

```typescript
// apps/gestor/src/screens/DashboardScreen.tsx
"""
Dashboard principal do gestor.

Exibe KPIs, alertas e metricas operacionais.
"""

import React, { useMemo } from 'react';
import { View, ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';

import {
  Card,
  KPICard,
  AlertList,
  OccupancyChart,
  FinancialSummary,
  Header,
  ErrorState,
  LoadingSkeleton,
} from '@shared-ui';
import { dashboardService } from '../services/dashboardService';
import { useRefreshOnFocus } from '@shared-hooks';

interface DashboardData {
  kpis: {
    colaboradores_ativos: number;
    postos_cobertos: number;
    taxa_ocupacao: number;
    faturamento_mes: number;
    inadimplencia: number;
    nps_score: number;
  };
  alertas: Alert[];
  grafico_ocupacao: OccupancyData[];
  financeiro: FinancialData;
}

export function DashboardScreen(): React.ReactElement {
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: dashboardService.getDashboard,
    staleTime: 60000, // 1 minuto
  });

  // Atualiza ao focar na tela
  useRefreshOnFocus(refetch);

  const kpiCards = useMemo(() => {
    if (!data?.kpis) return [];

    return [
      {
        title: 'Colaboradores Ativos',
        value: data.kpis.colaboradores_ativos,
        icon: 'people',
        color: '#4CAF50',
        format: 'number',
      },
      {
        title: 'Postos Cobertos',
        value: data.kpis.postos_cobertos,
        icon: 'location-on',
        color: '#2196F3',
        format: 'number',
      },
      {
        title: 'Taxa Ocupacao',
        value: data.kpis.taxa_ocupacao,
        icon: 'trending-up',
        color: '#FF9800',
        format: 'percent',
      },
      {
        title: 'Faturamento',
        value: data.kpis.faturamento_mes,
        icon: 'attach-money',
        color: '#9C27B0',
        format: 'currency',
      },
      {
        title: 'Inadimplencia',
        value: data.kpis.inadimplencia,
        icon: 'warning',
        color: data.kpis.inadimplencia > 5 ? '#F44336' : '#4CAF50',
        format: 'percent',
      },
      {
        title: 'NPS',
        value: data.kpis.nps_score,
        icon: 'star',
        color: '#FFC107',
        format: 'number',
      },
    ];
  }, [data?.kpis]);

  if (isLoading) {
    return <LoadingSkeleton type="dashboard" />;
  }

  if (isError) {
    return (
      <ErrorState
        message={error?.message || 'Erro ao carregar dashboard'}
        onRetry={refetch}
      />
    );
  }

  return (
    <View style={styles.container}>
      <Header
        title="Dashboard"
        subtitle={format(new Date(), 'dd/MM/yyyy HH:mm')}
        showNotifications
      />

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
        }
      >
        {/* KPIs Grid */}
        <View style={styles.kpiGrid}>
          {kpiCards.map((kpi, index) => (
            <KPICard
              key={index}
              title={kpi.title}
              value={kpi.value}
              icon={kpi.icon}
              color={kpi.color}
              format={kpi.format}
              style={styles.kpiCard}
            />
          ))}
        </View>

        {/* Alertas Criticos */}
        {data?.alertas && data.alertas.length > 0 && (
          <Card title="Alertas Criticos" style={styles.section}>
            <AlertList
              alerts={data.alertas}
              maxItems={5}
              onPress={(alert) => console.log('Alert pressed:', alert)}
            />
          </Card>
        )}

        {/* Grafico de Ocupacao */}
        <Card title="Ocupacao por Unidade" style={styles.section}>
          <OccupancyChart data={data?.grafico_ocupacao || []} />
        </Card>

        {/* Resumo Financeiro */}
        <Card title="Financeiro" style={styles.section}>
          <FinancialSummary data={data?.financeiro} />
        </Card>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  kpiGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  kpiCard: {
    width: '50%',
    padding: 8,
  },
  section: {
    margin: 16,
    marginTop: 0,
  },
});
```

---

## 5. APP CLIENTE

### 5.1 Funcionalidades

```
APP CLIENTE
===========

1. PORTAL
   - Visao geral do contrato
   - Status dos servicos
   - Avaliacao de qualidade

2. FINANCEIRO
   - Faturas abertas
   - Historico de pagamentos
   - 2a via de boleto
   - Pagamento via PIX

3. SOLICITACOES
   - Abertura de chamados
   - Acompanhamento
   - Historico

4. DOCUMENTOS
   - Contratos
   - Relatorios mensais
   - Certificados

5. COMUNICACAO
   - Chat com suporte
   - Notificacoes
   - Pesquisas
```

### 5.2 Tela de Faturas

```typescript
// apps/cliente/src/screens/FaturasScreen.tsx
"""
Tela de faturas do cliente.

Lista faturas, permite pagamento e download de boletos.
"""

import React, { useState, useCallback } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Alert,
  Linking,
} from 'react-native';
import { useQuery, useMutation } from '@tanstack/react-query';
import * as Clipboard from 'expo-clipboard';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';

import {
  FaturaCard,
  FilterTabs,
  EmptyState,
  LoadingSkeleton,
  BottomSheet,
  Button,
  QRCodePix,
} from '@shared-ui';
import { faturaService, Fatura } from '../services/faturaService';

type FaturaStatus = 'todas' | 'abertas' | 'pagas' | 'vencidas';

export function FaturasScreen(): React.ReactElement {
  const [statusFilter, setStatusFilter] = useState<FaturaStatus>('abertas');
  const [selectedFatura, setSelectedFatura] = useState<Fatura | null>(null);
  const [showPixSheet, setShowPixSheet] = useState(false);

  const { data: faturas, isLoading, refetch } = useQuery({
    queryKey: ['faturas', statusFilter],
    queryFn: () => faturaService.listar({ status: statusFilter }),
  });

  const gerarPixMutation = useMutation({
    mutationFn: faturaService.gerarPix,
    onSuccess: () => setShowPixSheet(true),
    onError: (error: Error) => {
      Alert.alert('Erro', error.message);
    },
  });

  /**
   * Abre boleto para visualizacao.
   *
   * @param fatura - Fatura selecionada
   */
  const abrirBoleto = useCallback(async (fatura: Fatura) => {
    try {
      const { url } = await faturaService.getBoletoUrl(fatura.id);
      await Linking.openURL(url);
    } catch (error) {
      Alert.alert('Erro', 'Nao foi possivel abrir o boleto');
    }
  }, []);

  /**
   * Compartilha boleto via apps do dispositivo.
   *
   * @param fatura - Fatura para compartilhar
   */
  const compartilharBoleto = useCallback(async (fatura: Fatura) => {
    try {
      const { url } = await faturaService.getBoletoUrl(fatura.id);
      const fileUri = `${FileSystem.cacheDirectory}boleto_${fatura.id}.pdf`;

      await FileSystem.downloadAsync(url, fileUri);

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/pdf',
          dialogTitle: 'Compartilhar Boleto',
        });
      }
    } catch (error) {
      Alert.alert('Erro', 'Nao foi possivel compartilhar o boleto');
    }
  }, []);

  /**
   * Copia codigo de barras para clipboard.
   *
   * @param fatura - Fatura com codigo
   */
  const copiarCodigoBarras = useCallback(async (fatura: Fatura) => {
    await Clipboard.setStringAsync(fatura.codigo_barras);
    Alert.alert('Copiado', 'Codigo de barras copiado para area de transferencia');
  }, []);

  /**
   * Gera QR Code PIX para pagamento.
   *
   * @param fatura - Fatura para pagar
   */
  const gerarPix = useCallback((fatura: Fatura) => {
    setSelectedFatura(fatura);
    gerarPixMutation.mutate(fatura.id);
  }, [gerarPixMutation]);

  const renderFatura = useCallback(({ item }: { item: Fatura }) => (
    <FaturaCard
      fatura={item}
      onAbrirBoleto={() => abrirBoleto(item)}
      onCompartilhar={() => compartilharBoleto(item)}
      onCopiarCodigo={() => copiarCodigoBarras(item)}
      onPagarPix={() => gerarPix(item)}
    />
  ), [abrirBoleto, compartilharBoleto, copiarCodigoBarras, gerarPix]);

  if (isLoading) {
    return <LoadingSkeleton type="list" count={5} />;
  }

  return (
    <View style={styles.container}>
      {/* Filtros */}
      <FilterTabs
        tabs={[
          { key: 'todas', label: 'Todas' },
          { key: 'abertas', label: 'Abertas' },
          { key: 'pagas', label: 'Pagas' },
          { key: 'vencidas', label: 'Vencidas' },
        ]}
        selected={statusFilter}
        onSelect={(tab) => setStatusFilter(tab as FaturaStatus)}
      />

      {/* Lista de Faturas */}
      <FlatList
        data={faturas}
        keyExtractor={(item) => item.id}
        renderItem={renderFatura}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <EmptyState
            icon="receipt"
            title="Nenhuma fatura"
            message="Nao ha faturas para exibir"
          />
        }
        refreshing={isLoading}
        onRefresh={refetch}
      />

      {/* Bottom Sheet - PIX */}
      <BottomSheet
        isVisible={showPixSheet}
        onClose={() => setShowPixSheet(false)}
        title="Pagamento via PIX"
      >
        {selectedFatura && gerarPixMutation.data && (
          <View style={styles.pixContainer}>
            <QRCodePix
              payload={gerarPixMutation.data.payload}
              valor={selectedFatura.valor}
              expiracao={gerarPixMutation.data.expiracao}
            />
            <Button
              title="Copiar Codigo PIX"
              icon="copy"
              onPress={() => {
                Clipboard.setStringAsync(gerarPixMutation.data.payload);
                Alert.alert('Copiado!', 'Codigo PIX copiado');
              }}
              style={styles.copyButton}
            />
          </View>
        )}
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  listContent: {
    padding: 16,
  },
  pixContainer: {
    padding: 20,
    alignItems: 'center',
  },
  copyButton: {
    marginTop: 20,
    width: '100%',
  },
});
```

---

## 6. APP TECNICO

### 6.1 Funcionalidades

```
APP TECNICO
===========

1. ORDENS DE SERVICO
   - Lista de OS atribuidas
   - Detalhes e instrucoes
   - Check-in/check-out
   - Status em tempo real

2. CHECKLIST
   - Checklist digital
   - Itens obrigatorios
   - Assinatura do cliente
   - Fotos de evidencia

3. MATERIAIS
   - Consulta de estoque
   - Requisicao de materiais
   - Baixa de itens

4. NAVEGACAO
   - Rota ate o cliente
   - Integracao Waze/Google Maps
   - Historico de visitas

5. DOCUMENTACAO
   - Manuais tecnicos
   - Procedimentos
   - Treinamentos
```

### 6.2 Tela de Ordem de Servico

```typescript
// apps/tecnico/src/screens/OrdemServicoScreen.tsx
"""
Tela de execucao de ordem de servico.

Permite checkin, checklist, fotos e assinatura.
"""

import React, { useState, useCallback, useRef } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as Location from 'expo-location';
import SignatureCanvas from 'react-native-signature-canvas';

import {
  Card,
  Button,
  ChecklistItem,
  PhotoGrid,
  Timer,
  ClientInfo,
  LoadingSkeleton,
  BottomSheet,
} from '@shared-ui';
import { osService, OrdemServico, ChecklistItemData } from '../services/osService';
import { useCamera } from '@shared-hooks';

type OSStatus = 'pendente' | 'em_andamento' | 'concluida' | 'cancelada';

export function OrdemServicoScreen(): React.ReactElement {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const queryClient = useQueryClient();
  const signatureRef = useRef<SignatureCanvas>(null);
  const { osId } = route.params;

  const [checklist, setChecklist] = useState<ChecklistItemData[]>([]);
  const [fotos, setFotos] = useState<string[]>([]);
  const [showSignature, setShowSignature] = useState(false);
  const [tempoInicio, setTempoInicio] = useState<Date | null>(null);

  const { takePhoto, selectFromGallery } = useCamera();

  const { data: os, isLoading } = useQuery<OrdemServico>({
    queryKey: ['ordem-servico', osId],
    queryFn: () => osService.getById(osId),
    onSuccess: (data) => {
      setChecklist(data.checklist || []);
      setFotos(data.fotos || []);
      if (data.status === 'em_andamento') {
        setTempoInicio(new Date(data.inicio_execucao));
      }
    },
  });

  const checkinMutation = useMutation({
    mutationFn: async () => {
      const location = await Location.getCurrentPositionAsync();
      return osService.checkin(osId, {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
    },
    onSuccess: () => {
      setTempoInicio(new Date());
      queryClient.invalidateQueries({ queryKey: ['ordem-servico', osId] });
      Alert.alert('Check-in realizado!');
    },
  });

  const concluirMutation = useMutation({
    mutationFn: osService.concluir,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] });
      Alert.alert('Sucesso', 'Ordem de servico concluida!', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    },
  });

  /**
   * Atualiza item do checklist.
   *
   * @param index - Indice do item
   * @param checked - Novo estado
   */
  const toggleChecklistItem = useCallback((index: number, checked: boolean) => {
    setChecklist((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], checked };
      return updated;
    });
  }, []);

  /**
   * Adiciona foto a OS.
   */
  const adicionarFoto = useCallback(async () => {
    Alert.alert('Adicionar Foto', 'Escolha a origem', [
      {
        text: 'Camera',
        onPress: async () => {
          const photo = await takePhoto();
          if (photo) {
            setFotos((prev) => [...prev, photo.uri]);
          }
        },
      },
      {
        text: 'Galeria',
        onPress: async () => {
          const photo = await selectFromGallery();
          if (photo) {
            setFotos((prev) => [...prev, photo.uri]);
          }
        },
      },
      { text: 'Cancelar', style: 'cancel' },
    ]);
  }, [takePhoto, selectFromGallery]);

  /**
   * Processa assinatura do cliente.
   *
   * @param signature - Assinatura em base64
   */
  const handleSignature = useCallback((signature: string) => {
    setShowSignature(false);

    // Verificar se todos itens obrigatorios foram marcados
    const pendentes = checklist.filter((item) => item.obrigatorio && !item.checked);
    if (pendentes.length > 0) {
      Alert.alert(
        'Checklist Incompleto',
        `Existem ${pendentes.length} itens obrigatorios pendentes`
      );
      return;
    }

    // Concluir OS
    concluirMutation.mutate({
      os_id: osId,
      checklist,
      fotos,
      assinatura_cliente: signature,
    });
  }, [checklist, fotos, osId, concluirMutation]);

  if (isLoading || !os) {
    return <LoadingSkeleton type="detail" />;
  }

  const isPendente = os.status === 'pendente';
  const isEmAndamento = os.status === 'em_andamento';

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Info do Cliente */}
        <ClientInfo
          cliente={os.cliente}
          endereco={os.endereco}
          onNavigate={() => {
            const url = `https://waze.com/ul?ll=${os.endereco.latitude},${os.endereco.longitude}&navigate=yes`;
            Linking.openURL(url);
          }}
        />

        {/* Timer */}
        {isEmAndamento && tempoInicio && (
          <Card style={styles.timerCard}>
            <Timer startTime={tempoInicio} label="Tempo de Execucao" />
          </Card>
        )}

        {/* Descricao */}
        <Card title="Descricao do Servico" style={styles.section}>
          <Text style={styles.descricao}>{os.descricao}</Text>
          {os.instrucoes && (
            <Text style={styles.instrucoes}>{os.instrucoes}</Text>
          )}
        </Card>

        {/* Checklist */}
        {isEmAndamento && (
          <Card title="Checklist" style={styles.section}>
            {checklist.map((item, index) => (
              <ChecklistItem
                key={item.id}
                label={item.descricao}
                checked={item.checked}
                required={item.obrigatorio}
                onToggle={(checked) => toggleChecklistItem(index, checked)}
              />
            ))}
          </Card>
        )}

        {/* Fotos */}
        {isEmAndamento && (
          <Card title="Fotos e Evidencias" style={styles.section}>
            <PhotoGrid
              photos={fotos}
              onAdd={adicionarFoto}
              onRemove={(index) => {
                setFotos((prev) => prev.filter((_, i) => i !== index));
              }}
              maxPhotos={10}
            />
          </Card>
        )}
      </ScrollView>

      {/* Acoes */}
      <View style={styles.actions}>
        {isPendente && (
          <Button
            title="Fazer Check-in"
            icon="login"
            variant="primary"
            size="large"
            loading={checkinMutation.isLoading}
            onPress={() => checkinMutation.mutate()}
          />
        )}
        {isEmAndamento && (
          <Button
            title="Concluir e Assinar"
            icon="check"
            variant="success"
            size="large"
            onPress={() => setShowSignature(true)}
          />
        )}
      </View>

      {/* Bottom Sheet - Assinatura */}
      <BottomSheet
        isVisible={showSignature}
        onClose={() => setShowSignature(false)}
        title="Assinatura do Cliente"
        height="70%"
      >
        <View style={styles.signatureContainer}>
          <SignatureCanvas
            ref={signatureRef}
            onOK={handleSignature}
            descriptionText="Assine acima"
            clearText="Limpar"
            confirmText="Confirmar"
            webStyle={signatureWebStyle}
          />
        </View>
      </BottomSheet>
    </View>
  );
}

const signatureWebStyle = `.m-signature-pad { box-shadow: none; border: none; }
  .m-signature-pad--body { border: 1px solid #ccc; }`;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  section: {
    margin: 16,
    marginTop: 0,
  },
  timerCard: {
    margin: 16,
    backgroundColor: '#e3f2fd',
  },
  descricao: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  instrucoes: {
    fontSize: 14,
    color: '#666',
    marginTop: 12,
    fontStyle: 'italic',
  },
  actions: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  signatureContainer: {
    flex: 1,
    padding: 16,
  },
});
```

---

## 7. APP VENDEDOR

### 7.1 Funcionalidades

```
APP VENDEDOR
============

1. CRM MOBILE
   - Pipeline de vendas
   - Leads e oportunidades
   - Historico de interacoes

2. PROPOSTAS
   - Geracao de propostas
   - Catalogo de servicos
   - Precificacao automatica
   - Envio por WhatsApp/Email

3. AGENDA
   - Visitas agendadas
   - Lembretes
   - Check-in em visitas

4. METAS
   - Metas individuais
   - Ranking da equipe
   - Comissoes

5. DOCUMENTOS
   - Apresentacoes
   - Cases de sucesso
   - Materiais de apoio
```

### 7.2 Tela de Pipeline

```typescript
// apps/vendedor/src/screens/PipelineScreen.tsx
"""
Tela de pipeline de vendas.

Visualizacao Kanban das oportunidades.
"""

import React, { useState, useCallback, useMemo } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import DraggableFlatList, { RenderItemParams } from 'react-native-draggable-flatlist';

import {
  Card,
  OpportunityCard,
  StageHeader,
  LoadingSkeleton,
  FAB,
} from '@shared-ui';
import { oportunidadeService, Oportunidade } from '../services/oportunidadeService';

interface Stage {
  id: string;
  nome: string;
  cor: string;
  oportunidades: Oportunidade[];
  valor_total: number;
}

const SCREEN_WIDTH = Dimensions.get('window').width;
const STAGE_WIDTH = SCREEN_WIDTH * 0.8;

export function PipelineScreen(): React.ReactElement {
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);

  const { data: stages, isLoading } = useQuery<Stage[]>({
    queryKey: ['pipeline'],
    queryFn: oportunidadeService.getPipeline,
  });

  const moverMutation = useMutation({
    mutationFn: oportunidadeService.moverEstagio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pipeline'] });
    },
  });

  /**
   * Move oportunidade para novo estagio.
   *
   * @param oportunidadeId - ID da oportunidade
   * @param novoEstagioId - ID do novo estagio
   */
  const moverOportunidade = useCallback((
    oportunidadeId: string,
    novoEstagioId: string
  ) => {
    moverMutation.mutate({ oportunidadeId, novoEstagioId });
  }, [moverMutation]);

  /**
   * Renderiza card de oportunidade draggable.
   */
  const renderOportunidade = useCallback(({
    item,
    drag,
    isActive,
  }: RenderItemParams<Oportunidade>) => (
    <OpportunityCard
      oportunidade={item}
      onLongPress={drag}
      isActive={isActive}
      onPress={() => {
        // Navegar para detalhes
      }}
    />
  ), []);

  /**
   * Calcula totais por estagio.
   */
  const totais = useMemo(() => {
    if (!stages) return { quantidade: 0, valor: 0 };

    return stages.reduce(
      (acc, stage) => ({
        quantidade: acc.quantidade + stage.oportunidades.length,
        valor: acc.valor + stage.valor_total,
      }),
      { quantidade: 0, valor: 0 }
    );
  }, [stages]);

  if (isLoading) {
    return <LoadingSkeleton type="kanban" />;
  }

  return (
    <View style={styles.container}>
      {/* Resumo */}
      <View style={styles.summary}>
        <Card style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total Oportunidades</Text>
          <Text style={styles.summaryValue}>{totais.quantidade}</Text>
        </Card>
        <Card style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Valor Total</Text>
          <Text style={styles.summaryValue}>
            {formatCurrency(totais.valor)}
          </Text>
        </Card>
      </View>

      {/* Kanban Board */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.kanbanContainer}
        snapToInterval={STAGE_WIDTH + 12}
        decelerationRate="fast"
      >
        {stages?.map((stage) => (
          <View key={stage.id} style={styles.stageColumn}>
            <StageHeader
              nome={stage.nome}
              cor={stage.cor}
              quantidade={stage.oportunidades.length}
              valor={stage.valor_total}
            />
            <DraggableFlatList
              data={stage.oportunidades}
              keyExtractor={(item) => item.id}
              renderItem={renderOportunidade}
              onDragEnd={({ data, from, to }) => {
                if (from !== to) {
                  // Atualizar ordem local e sincronizar
                }
              }}
              containerStyle={styles.stageList}
            />
          </View>
        ))}
      </ScrollView>

      {/* FAB - Nova Oportunidade */}
      <FAB
        icon="add"
        onPress={() => {
          // Navegar para criar oportunidade
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summary: {
    flexDirection: 'row',
    padding: 16,
  },
  summaryCard: {
    flex: 1,
    marginHorizontal: 4,
    alignItems: 'center',
    padding: 12,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  kanbanContainer: {
    paddingHorizontal: 8,
  },
  stageColumn: {
    width: STAGE_WIDTH,
    marginHorizontal: 6,
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
  },
  stageList: {
    flex: 1,
    padding: 8,
  },
});
```

---

## 8. COMPONENTES COMPARTILHADOS

### 8.1 Design System

```typescript
// packages/shared-ui/src/theme/index.ts
"""
Tema e design tokens compartilhados.

Define cores, espacamentos e tipografia.
"""

export const theme = {
  colors: {
    primary: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',  // Principal
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1',
    },
    secondary: {
      500: '#9c27b0',
    },
    success: {
      500: '#4caf50',
    },
    warning: {
      500: '#ff9800',
    },
    error: {
      500: '#f44336',
    },
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    },
    background: '#ffffff',
    surface: '#ffffff',
    text: {
      primary: '#212121',
      secondary: '#757575',
      disabled: '#9e9e9e',
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    xl: 24,
    full: 9999,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold',
      lineHeight: 40,
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
      lineHeight: 32,
    },
    h3: {
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 28,
    },
    body1: {
      fontSize: 16,
      fontWeight: 'normal',
      lineHeight: 24,
    },
    body2: {
      fontSize: 14,
      fontWeight: 'normal',
      lineHeight: 20,
    },
    caption: {
      fontSize: 12,
      fontWeight: 'normal',
      lineHeight: 16,
    },
  },
  shadows: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.15,
      shadowRadius: 4,
      elevation: 4,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 8,
    },
  },
};
```

### 8.2 Componente Button

```typescript
// packages/shared-ui/src/components/Button.tsx
"""
Botao reutilizavel com variantes.

Suporta icones, loading e diferentes tamanhos.
"""

import React from 'react';
import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { theme } from '../theme';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'success' | 'danger';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: string;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

const variantStyles: Record<ButtonVariant, { container: ViewStyle; text: TextStyle }> = {
  primary: {
    container: { backgroundColor: theme.colors.primary[500] },
    text: { color: '#fff' },
  },
  secondary: {
    container: { backgroundColor: theme.colors.secondary[500] },
    text: { color: '#fff' },
  },
  outline: {
    container: {
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: theme.colors.primary[500],
    },
    text: { color: theme.colors.primary[500] },
  },
  ghost: {
    container: { backgroundColor: 'transparent' },
    text: { color: theme.colors.primary[500] },
  },
  success: {
    container: { backgroundColor: theme.colors.success[500] },
    text: { color: '#fff' },
  },
  danger: {
    container: { backgroundColor: theme.colors.error[500] },
    text: { color: '#fff' },
  },
};

const sizeStyles: Record<ButtonSize, { container: ViewStyle; text: TextStyle; icon: number }> = {
  small: {
    container: { paddingVertical: 8, paddingHorizontal: 12 },
    text: { fontSize: 14 },
    icon: 16,
  },
  medium: {
    container: { paddingVertical: 12, paddingHorizontal: 16 },
    text: { fontSize: 16 },
    icon: 20,
  },
  large: {
    container: { paddingVertical: 16, paddingHorizontal: 24 },
    text: { fontSize: 18 },
    icon: 24,
  },
};

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  style,
}: ButtonProps): React.ReactElement {
  const variantStyle = variantStyles[variant];
  const sizeStyle = sizeStyles[size];
  const isDisabled = disabled || loading;

  const renderIcon = () => {
    if (loading) {
      return (
        <ActivityIndicator
          size="small"
          color={variantStyle.text.color}
          style={iconPosition === 'left' ? styles.iconLeft : styles.iconRight}
        />
      );
    }

    if (icon) {
      return (
        <Icon
          name={icon}
          size={sizeStyle.icon}
          color={variantStyle.text.color as string}
          style={iconPosition === 'left' ? styles.iconLeft : styles.iconRight}
        />
      );
    }

    return null;
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      style={[
        styles.container,
        variantStyle.container,
        sizeStyle.container,
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {iconPosition === 'left' && renderIcon()}
      <Text
        style={[
          styles.text,
          variantStyle.text,
          sizeStyle.text,
          isDisabled && styles.disabledText,
        ]}
      >
        {title}
      </Text>
      {iconPosition === 'right' && renderIcon()}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.borderRadius.md,
  },
  text: {
    fontWeight: '600',
  },
  disabled: {
    opacity: 0.5,
  },
  disabledText: {
    opacity: 0.7,
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
});
```

---

## 9. OFFLINE FIRST

### 9.1 Sync Engine

```typescript
// packages/sync-engine/src/SyncEngine.ts
"""
Motor de sincronizacao offline-first.

Gerencia fila de operacoes e sincronizacao com backend.
"""

import { Database } from '@nozbe/watermelondb';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { v4 as uuidv4 } from 'uuid';

import { apiClient } from '@shared-hooks';

interface SyncOperation {
  id: string;
  table: string;
  operation: 'create' | 'update' | 'delete';
  record_id: string;
  data: Record<string, any>;
  created_at: Date;
  attempts: number;
  last_error?: string;
}

interface SyncConfig {
  database: Database;
  tables: string[];
  batchSize?: number;
  maxRetries?: number;
  retryDelay?: number;
}

export class SyncEngine {
  private database: Database;
  private tables: string[];
  private batchSize: number;
  private maxRetries: number;
  private retryDelay: number;
  private isOnline: boolean = true;
  private isSyncing: boolean = false;
  private syncQueue: SyncOperation[] = [];

  constructor(config: SyncConfig) {
    this.database = config.database;
    this.tables = config.tables;
    this.batchSize = config.batchSize || 50;
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 5000;

    this.setupNetworkListener();
    this.loadPendingOperations();
  }

  /**
   * Configura listener de conectividade.
   */
  private setupNetworkListener(): void {
    NetInfo.addEventListener((state: NetInfoState) => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;

      if (wasOffline && this.isOnline) {
        console.log('[SyncEngine] Conexao restaurada, iniciando sync');
        this.sync();
      }
    });
  }

  /**
   * Carrega operacoes pendentes do storage local.
   */
  private async loadPendingOperations(): Promise<void> {
    try {
      const pendingOps = await this.database
        .get('sync_queue')
        .query()
        .fetch();

      this.syncQueue = pendingOps.map((op) => ({
        id: op.id,
        table: op.table,
        operation: op.operation,
        record_id: op.record_id,
        data: JSON.parse(op.data),
        created_at: new Date(op.created_at),
        attempts: op.attempts,
        last_error: op.last_error,
      }));

      console.log(`[SyncEngine] ${this.syncQueue.length} operacoes pendentes`);
    } catch (error) {
      console.error('[SyncEngine] Erro ao carregar operacoes:', error);
    }
  }

  /**
   * Adiciona operacao na fila de sync.
   *
   * @param table - Nome da tabela
   * @param operation - Tipo de operacao
   * @param recordId - ID do registro
   * @param data - Dados do registro
   */
  async enqueue(
    table: string,
    operation: SyncOperation['operation'],
    recordId: string,
    data: Record<string, any>
  ): Promise<void> {
    const syncOp: SyncOperation = {
      id: uuidv4(),
      table,
      operation,
      record_id: recordId,
      data,
      created_at: new Date(),
      attempts: 0,
    };

    // Salvar no banco local
    await this.database.write(async () => {
      await this.database.get('sync_queue').create((record) => {
        record._raw.id = syncOp.id;
        record.table = syncOp.table;
        record.operation = syncOp.operation;
        record.record_id = syncOp.record_id;
        record.data = JSON.stringify(syncOp.data);
        record.created_at = syncOp.created_at.toISOString();
        record.attempts = 0;
      });
    });

    this.syncQueue.push(syncOp);

    // Tentar sync imediato se online
    if (this.isOnline && !this.isSyncing) {
      this.sync();
    }
  }

  /**
   * Executa sincronizacao com backend.
   */
  async sync(): Promise<void> {
    if (this.isSyncing || !this.isOnline || this.syncQueue.length === 0) {
      return;
    }

    this.isSyncing = true;
    console.log(`[SyncEngine] Iniciando sync de ${this.syncQueue.length} operacoes`);

    try {
      // Processar em batches
      const batches = this.chunkArray(this.syncQueue, this.batchSize);

      for (const batch of batches) {
        await this.processBatch(batch);
      }

      // Pull de atualizacoes do servidor
      await this.pullUpdates();

      console.log('[SyncEngine] Sync concluido com sucesso');
    } catch (error) {
      console.error('[SyncEngine] Erro no sync:', error);
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Processa batch de operacoes.
   *
   * @param batch - Lista de operacoes
   */
  private async processBatch(batch: SyncOperation[]): Promise<void> {
    for (const op of batch) {
      try {
        await this.processOperation(op);
        await this.removeFromQueue(op.id);
      } catch (error) {
        await this.handleOperationError(op, error);
      }
    }
  }

  /**
   * Processa operacao individual.
   *
   * @param op - Operacao a processar
   */
  private async processOperation(op: SyncOperation): Promise<void> {
    const endpoint = `/api/v1/${op.table}`;

    switch (op.operation) {
      case 'create':
        await apiClient.post(endpoint, op.data);
        break;
      case 'update':
        await apiClient.put(`${endpoint}/${op.record_id}`, op.data);
        break;
      case 'delete':
        await apiClient.delete(`${endpoint}/${op.record_id}`);
        break;
    }
  }

  /**
   * Trata erro de operacao.
   *
   * @param op - Operacao que falhou
   * @param error - Erro ocorrido
   */
  private async handleOperationError(
    op: SyncOperation,
    error: unknown
  ): Promise<void> {
    op.attempts += 1;
    op.last_error = error instanceof Error ? error.message : 'Erro desconhecido';

    if (op.attempts >= this.maxRetries) {
      // Mover para fila de erros
      await this.moveToErrorQueue(op);
      await this.removeFromQueue(op.id);
    } else {
      // Atualizar tentativas
      await this.database.write(async () => {
        const record = await this.database.get('sync_queue').find(op.id);
        await record.update((r) => {
          r.attempts = op.attempts;
          r.last_error = op.last_error;
        });
      });
    }
  }

  /**
   * Busca atualizacoes do servidor.
   */
  private async pullUpdates(): Promise<void> {
    for (const table of this.tables) {
      try {
        const lastSync = await this.getLastSyncTime(table);
        const { data } = await apiClient.get(`/api/v1/${table}/sync`, {
          params: { since: lastSync?.toISOString() },
        });

        await this.applyUpdates(table, data.records);
        await this.setLastSyncTime(table, new Date());
      } catch (error) {
        console.error(`[SyncEngine] Erro ao pull ${table}:`, error);
      }
    }
  }

  /**
   * Aplica atualizacoes do servidor no banco local.
   *
   * @param table - Nome da tabela
   * @param records - Registros a aplicar
   */
  private async applyUpdates(
    table: string,
    records: Record<string, any>[]
  ): Promise<void> {
    await this.database.write(async () => {
      const collection = this.database.get(table);

      for (const record of records) {
        try {
          const existing = await collection.find(record.id);
          await existing.update((r) => {
            Object.assign(r._raw, record);
          });
        } catch {
          // Registro nao existe, criar
          await collection.create((r) => {
            Object.assign(r._raw, record);
          });
        }
      }
    });
  }

  /**
   * Divide array em chunks.
   */
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  // ... metodos auxiliares
}
```

---

## 10. PUSH NOTIFICATIONS

### 10.1 Configuracao FCM

```typescript
// packages/push-notifications/src/PushService.ts
"""
Servico de notificacoes push via Firebase.

Gerencia tokens, permissoes e handlers.
"""

import messaging, { FirebaseMessagingTypes } from '@react-native-firebase/messaging';
import notifee, { AndroidImportance, EventType } from '@notifee/react-native';
import { Platform } from 'react-native';

import { apiClient } from '@shared-hooks';

interface NotificationPayload {
  title: string;
  body: string;
  data?: Record<string, string>;
}

type NotificationHandler = (payload: NotificationPayload) => void;

export class PushService {
  private static instance: PushService;
  private token: string | null = null;
  private handlers: Map<string, NotificationHandler> = new Map();

  private constructor() {
    this.initialize();
  }

  static getInstance(): PushService {
    if (!PushService.instance) {
      PushService.instance = new PushService();
    }
    return PushService.instance;
  }

  /**
   * Inicializa servico de push.
   */
  private async initialize(): Promise<void> {
    // Criar canal Android
    if (Platform.OS === 'android') {
      await notifee.createChannel({
        id: 'default',
        name: 'Notificacoes',
        importance: AndroidImportance.HIGH,
        vibration: true,
      });

      await notifee.createChannel({
        id: 'alerts',
        name: 'Alertas Criticos',
        importance: AndroidImportance.HIGH,
        vibration: true,
        lights: true,
        lightColor: '#FF0000',
      });
    }

    // Handlers de mensagens
    messaging().onMessage(this.handleForegroundMessage.bind(this));
    messaging().setBackgroundMessageHandler(this.handleBackgroundMessage.bind(this));

    // Handler de interacao com notificacao
    notifee.onForegroundEvent(({ type, detail }) => {
      if (type === EventType.PRESS && detail.notification?.data) {
        this.handleNotificationPress(detail.notification.data as Record<string, string>);
      }
    });
  }

  /**
   * Solicita permissao e registra token.
   *
   * @returns Token FCM ou null
   */
  async requestPermission(): Promise<string | null> {
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (!enabled) {
      console.log('[Push] Permissao negada');
      return null;
    }

    try {
      this.token = await messaging().getToken();
      await this.registerToken(this.token);
      console.log('[Push] Token registrado:', this.token.substring(0, 20) + '...');

      // Listener para refresh de token
      messaging().onTokenRefresh(async (newToken) => {
        this.token = newToken;
        await this.registerToken(newToken);
      });

      return this.token;
    } catch (error) {
      console.error('[Push] Erro ao obter token:', error);
      return null;
    }
  }

  /**
   * Registra token no backend.
   *
   * @param token - Token FCM
   */
  private async registerToken(token: string): Promise<void> {
    try {
      await apiClient.post('/api/v1/push/register', {
        token,
        platform: Platform.OS,
        device_id: await getDeviceId(),
      });
    } catch (error) {
      console.error('[Push] Erro ao registrar token:', error);
    }
  }

  /**
   * Trata mensagem em foreground.
   *
   * @param remoteMessage - Mensagem recebida
   */
  private async handleForegroundMessage(
    remoteMessage: FirebaseMessagingTypes.RemoteMessage
  ): Promise<void> {
    const { notification, data } = remoteMessage;

    if (!notification) return;

    // Exibir notificacao local
    await notifee.displayNotification({
      title: notification.title,
      body: notification.body,
      data: data as Record<string, string>,
      android: {
        channelId: data?.priority === 'high' ? 'alerts' : 'default',
        smallIcon: 'ic_notification',
        pressAction: { id: 'default' },
      },
      ios: {
        foregroundPresentationOptions: {
          alert: true,
          badge: true,
          sound: true,
        },
      },
    });

    // Executar handler customizado
    const type = data?.type as string;
    if (type && this.handlers.has(type)) {
      this.handlers.get(type)!({
        title: notification.title || '',
        body: notification.body || '',
        data: data as Record<string, string>,
      });
    }
  }

  /**
   * Trata mensagem em background.
   *
   * @param remoteMessage - Mensagem recebida
   */
  private async handleBackgroundMessage(
    remoteMessage: FirebaseMessagingTypes.RemoteMessage
  ): Promise<void> {
    console.log('[Push] Mensagem em background:', remoteMessage.notification?.title);
    // Notificacao ja e exibida automaticamente pelo sistema
  }

  /**
   * Trata clique em notificacao.
   *
   * @param data - Dados da notificacao
   */
  private handleNotificationPress(data: Record<string, string>): void {
    const type = data.type;

    // Navegar baseado no tipo
    switch (type) {
      case 'ponto':
        // Navegar para tela de ponto
        break;
      case 'aprovacao':
        // Navegar para aprovacoes
        break;
      case 'os':
        // Navegar para ordem de servico
        break;
      default:
        // Navegar para home
        break;
    }
  }

  /**
   * Registra handler para tipo de notificacao.
   *
   * @param type - Tipo de notificacao
   * @param handler - Funcao handler
   */
  registerHandler(type: string, handler: NotificationHandler): void {
    this.handlers.set(type, handler);
  }

  /**
   * Remove handler.
   *
   * @param type - Tipo de notificacao
   */
  unregisterHandler(type: string): void {
    this.handlers.delete(type);
  }
}

export const pushService = PushService.getInstance();
```

---

## 11. BIOMETRIA E SEGURANCA

### 11.1 Autenticacao Biometrica

```typescript
// packages/biometric-auth/src/BiometricAuth.ts
"""
Servico de autenticacao biometrica.

Suporta Face ID, Touch ID e reconhecimento facial.
"""

import ReactNativeBiometrics, { BiometryType } from 'react-native-biometrics';
import * as Keychain from 'react-native-keychain';
import { Platform } from 'react-native';

interface BiometricResult {
  success: boolean;
  error?: string;
}

interface BiometricCapabilities {
  available: boolean;
  biometryType: BiometryType | null;
  enrolled: boolean;
}

export class BiometricAuth {
  private static instance: BiometricAuth;
  private rnBiometrics: ReactNativeBiometrics;

  private constructor() {
    this.rnBiometrics = new ReactNativeBiometrics({
      allowDeviceCredentials: true,
    });
  }

  static getInstance(): BiometricAuth {
    if (!BiometricAuth.instance) {
      BiometricAuth.instance = new BiometricAuth();
    }
    return BiometricAuth.instance;
  }

  /**
   * Verifica capacidades biometricas do dispositivo.
   *
   * @returns Informacoes de biometria
   */
  async checkCapabilities(): Promise<BiometricCapabilities> {
    try {
      const { available, biometryType } = await this.rnBiometrics.isSensorAvailable();

      return {
        available,
        biometryType: biometryType || null,
        enrolled: available,
      };
    } catch (error) {
      return {
        available: false,
        biometryType: null,
        enrolled: false,
      };
    }
  }

  /**
   * Solicita autenticacao biometrica.
   *
   * @param promptMessage - Mensagem para o usuario
   * @returns Resultado da autenticacao
   */
  async authenticate(promptMessage: string): Promise<BiometricResult> {
    try {
      const { available } = await this.rnBiometrics.isSensorAvailable();

      if (!available) {
        return {
          success: false,
          error: 'Biometria nao disponivel',
        };
      }

      const { success } = await this.rnBiometrics.simplePrompt({
        promptMessage,
        cancelButtonText: 'Cancelar',
      });

      return { success };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      };
    }
  }

  /**
   * Gera par de chaves biometricas.
   *
   * @returns Chave publica em base64
   */
  async createKeys(): Promise<string | null> {
    try {
      const { publicKey } = await this.rnBiometrics.createKeys();
      return publicKey;
    } catch (error) {
      console.error('[Biometric] Erro ao criar chaves:', error);
      return null;
    }
  }

  /**
   * Assina payload com chave biometrica.
   *
   * @param payload - Dados a assinar
   * @param promptMessage - Mensagem para o usuario
   * @returns Assinatura em base64
   */
  async createSignature(
    payload: string,
    promptMessage: string
  ): Promise<string | null> {
    try {
      const { success, signature } = await this.rnBiometrics.createSignature({
        promptMessage,
        payload,
        cancelButtonText: 'Cancelar',
      });

      return success ? signature : null;
    } catch (error) {
      console.error('[Biometric] Erro ao assinar:', error);
      return null;
    }
  }

  /**
   * Armazena credenciais com protecao biometrica.
   *
   * @param username - Usuario
   * @param password - Senha
   */
  async storeCredentials(username: string, password: string): Promise<boolean> {
    try {
      await Keychain.setGenericPassword(username, password, {
        accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
        accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED,
        authenticationType: Keychain.AUTHENTICATION_TYPE.BIOMETRICS,
      });
      return true;
    } catch (error) {
      console.error('[Biometric] Erro ao armazenar credenciais:', error);
      return false;
    }
  }

  /**
   * Recupera credenciais com autenticacao biometrica.
   *
   * @param promptMessage - Mensagem para o usuario
   * @returns Credenciais ou null
   */
  async getCredentials(
    promptMessage: string
  ): Promise<{ username: string; password: string } | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        authenticationPrompt: {
          title: 'Autenticacao',
          subtitle: promptMessage,
          cancel: 'Cancelar',
        },
      });

      if (credentials) {
        return {
          username: credentials.username,
          password: credentials.password,
        };
      }
      return null;
    } catch (error) {
      console.error('[Biometric] Erro ao recuperar credenciais:', error);
      return null;
    }
  }

  /**
   * Remove credenciais armazenadas.
   */
  async clearCredentials(): Promise<boolean> {
    try {
      await Keychain.resetGenericPassword();
      return true;
    } catch (error) {
      console.error('[Biometric] Erro ao limpar credenciais:', error);
      return false;
    }
  }
}

export const biometricAuth = BiometricAuth.getInstance();
```

---

## 12. TESTES MOBILE

### 12.1 Configuracao Jest

```javascript
// jest.config.js
module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|react-native-.*|@react-navigation|@tanstack/react-query)/)',
  ],
  moduleNameMapper: {
    '^@shared-ui$': '<rootDir>/packages/shared-ui/src',
    '^@shared-hooks$': '<rootDir>/packages/shared-hooks/src',
    '^@sync-engine$': '<rootDir>/packages/sync-engine/src',
    '^@biometric-auth$': '<rootDir>/packages/biometric-auth/src',
  },
  collectCoverageFrom: [
    'apps/**/*.{ts,tsx}',
    'packages/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### 12.2 Testes de Componentes

```typescript
// packages/shared-ui/src/components/__tests__/Button.test.tsx
"""
Testes do componente Button.

Verifica renderizacao, interacoes e variantes.
"""

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';

import { Button } from '../Button';

describe('Button', () => {
  it('renderiza corretamente com titulo', () => {
    const { getByText } = render(
      <Button title="Clique aqui" onPress={() => {}} />
    );

    expect(getByText('Clique aqui')).toBeTruthy();
  });

  it('chama onPress quando clicado', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <Button title="Clique" onPress={onPressMock} />
    );

    fireEvent.press(getByText('Clique'));
    expect(onPressMock).toHaveBeenCalledTimes(1);
  });

  it('nao chama onPress quando disabled', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <Button title="Clique" onPress={onPressMock} disabled />
    );

    fireEvent.press(getByText('Clique'));
    expect(onPressMock).not.toHaveBeenCalled();
  });

  it('exibe loading indicator quando loading=true', () => {
    const { queryByTestId, getByText } = render(
      <Button title="Salvando" onPress={() => {}} loading />
    );

    // Texto ainda visivel
    expect(getByText('Salvando')).toBeTruthy();
  });

  describe('variantes', () => {
    it('aplica estilo primary corretamente', () => {
      const { getByTestId } = render(
        <Button title="Primary" onPress={() => {}} variant="primary" />
      );
      // Verificar estilos aplicados
    });

    it('aplica estilo outline corretamente', () => {
      const { getByTestId } = render(
        <Button title="Outline" onPress={() => {}} variant="outline" />
      );
      // Verificar estilos aplicados
    });
  });

  describe('tamanhos', () => {
    it('aplica tamanho small corretamente', () => {
      const { getByTestId } = render(
        <Button title="Small" onPress={() => {}} size="small" />
      );
      // Verificar padding reduzido
    });

    it('aplica tamanho large corretamente', () => {
      const { getByTestId } = render(
        <Button title="Large" onPress={() => {}} size="large" />
      );
      // Verificar padding aumentado
    });
  });

  describe('icones', () => {
    it('renderiza icone a esquerda', () => {
      const { getByTestId } = render(
        <Button title="Salvar" onPress={() => {}} icon="save" />
      );
      // Verificar icone presente
    });

    it('renderiza icone a direita', () => {
      const { getByTestId } = render(
        <Button
          title="Proximo"
          onPress={() => {}}
          icon="arrow-forward"
          iconPosition="right"
        />
      );
      // Verificar posicao do icone
    });
  });
});
```

### 12.3 Testes E2E com Detox

```typescript
// e2e/colaborador/ponto.e2e.ts
"""
Testes E2E do fluxo de ponto.

Testa registro de ponto com biometria.
"""

import { device, element, by, expect } from 'detox';

describe('Registro de Ponto', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('deve fazer login com sucesso', async () => {
    await element(by.id('input-email')).typeText('joao@empresa.com');
    await element(by.id('input-senha')).typeText('senha123');
    await element(by.id('btn-login')).tap();

    await expect(element(by.id('screen-home'))).toBeVisible();
  });

  it('deve navegar para tela de ponto', async () => {
    await element(by.id('tab-ponto')).tap();
    await expect(element(by.id('screen-ponto'))).toBeVisible();
  });

  it('deve exibir preview da camera', async () => {
    await expect(element(by.id('camera-preview'))).toBeVisible();
  });

  it('deve registrar entrada com sucesso', async () => {
    // Simular biometria
    await device.setBiometricEnrollment(true);

    await element(by.id('btn-entrada')).tap();

    // Aguardar modal de biometria
    await device.matchBiometric();

    // Verificar sucesso
    await expect(element(by.text('Ponto registrado com sucesso!'))).toBeVisible();
  });

  it('deve exibir historico de registros', async () => {
    await expect(element(by.id('lista-registros'))).toBeVisible();
    await expect(element(by.id('registro-entrada'))).toBeVisible();
  });

  it('deve registrar saida com sucesso', async () => {
    await element(by.id('btn-saida')).tap();
    await device.matchBiometric();

    await expect(element(by.text('Ponto registrado com sucesso!'))).toBeVisible();
    await expect(element(by.id('registro-saida'))).toBeVisible();
  });

  it('deve funcionar offline', async () => {
    // Desabilitar rede
    await device.setURLBlacklist(['.*']);

    await element(by.id('btn-entrada')).tap();
    await device.matchBiometric();

    // Deve mostrar indicador de pendente
    await expect(element(by.id('sync-pendente'))).toBeVisible();

    // Reabilitar rede
    await device.setURLBlacklist([]);

    // Aguardar sync
    await waitFor(element(by.id('sync-pendente')))
      .not.toBeVisible()
      .withTimeout(10000);
  });
});
```

---

## CHECKLIST DO SPRINT

```
SPRINT 31-34 - MOBILE
=====================

[ ] Estrutura monorepo configurada
[ ] Packages compartilhados criados
[ ] App Colaborador implementado
    [ ] Registro de ponto biometrico
    [ ] Visualizacao de escala
    [ ] Solicitacoes
    [ ] Holerite digital
[ ] App Gestor implementado
    [ ] Dashboard
    [ ] Aprovacoes
    [ ] Gestao de equipe
[ ] App Cliente implementado
    [ ] Portal
    [ ] Faturas
    [ ] Chamados
[ ] App Tecnico implementado
    [ ] Ordens de servico
    [ ] Checklist
    [ ] Assinatura digital
[ ] App Vendedor implementado
    [ ] Pipeline CRM
    [ ] Propostas
    [ ] Agenda
[ ] Sync Engine funcionando
[ ] Push Notifications configurado
[ ] Biometria implementada
[ ] Testes unitarios >= 80%
[ ] Testes E2E passando
[ ] Apps publicados na store (TestFlight/Play Console)
```

---

*Skill Mobile - ERP Conecta Mais Fase 2*
*"Mobile-first para produtividade em campo"*
