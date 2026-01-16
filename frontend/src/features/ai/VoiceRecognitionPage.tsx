'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Play,
  Pause,
  Square,
  Upload,
  Download,
  FileAudio,
  Clock,
  Languages,
  Settings,
  Search,
  Filter,
  Trash2,
  Eye,
  Copy,
  Check,
  MoreVertical,
  Sparkles,
  AudioWaveform,
  Volume2,
  VolumeX,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Progress,
  Dropdown,
  EmptyState,
} from '@/design-system/components';

// Types
interface Transcription {
  id: string;
  filename: string;
  duration: number;
  language: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  createdAt: string;
  completedAt?: string;
  text?: string;
  confidence: number;
  speakers?: Speaker[];
}

interface Speaker {
  id: string;
  name: string;
  segments: TranscriptSegment[];
}

interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  confidence: number;
}

// Mock Data
const mockTranscriptions: Transcription[] = [
  {
    id: '1',
    filename: 'reuniao_planejamento.mp3',
    duration: 3600,
    language: 'pt-BR',
    status: 'completed',
    createdAt: '2026-01-16T10:00:00',
    completedAt: '2026-01-16T10:15:00',
    confidence: 96.5,
    text: 'Bom dia a todos. Vamos começar a reunião de planejamento. O primeiro ponto da pauta é...',
    speakers: [
      {
        id: '1',
        name: 'Speaker 1',
        segments: [
          { start: 0, end: 5, text: 'Bom dia a todos.', confidence: 98 },
          { start: 5, end: 12, text: 'Vamos começar a reunião de planejamento.', confidence: 97 },
        ],
      },
    ],
  },
  {
    id: '2',
    filename: 'entrevista_candidato.wav',
    duration: 1800,
    language: 'pt-BR',
    status: 'completed',
    createdAt: '2026-01-15T14:30:00',
    completedAt: '2026-01-15T14:38:00',
    confidence: 94.2,
    text: 'Olá, seja bem-vindo à entrevista. Pode começar se apresentando...',
  },
  {
    id: '3',
    filename: 'call_cliente.mp3',
    duration: 900,
    language: 'pt-BR',
    status: 'processing',
    createdAt: '2026-01-16T11:00:00',
    confidence: 0,
  },
  {
    id: '4',
    filename: 'apresentacao_produto.mp3',
    duration: 2700,
    language: 'en-US',
    status: 'pending',
    createdAt: '2026-01-16T11:30:00',
    confidence: 0,
  },
];

const statusConfig = {
  pending: { label: 'Pendente', color: 'secondary' as const, icon: Clock },
  processing: { label: 'Processando', color: 'warning' as const, icon: RefreshCw },
  completed: { label: 'Concluído', color: 'success' as const, icon: CheckCircle2 },
  error: { label: 'Erro', color: 'danger' as const, icon: AlertCircle },
};

const supportedLanguages = [
  { code: 'pt-BR', name: 'Português (Brasil)' },
  { code: 'en-US', name: 'English (US)' },
  { code: 'es-ES', name: 'Español' },
  { code: 'fr-FR', name: 'Français' },
  { code: 'de-DE', name: 'Deutsch' },
];

export function VoiceRecognitionPage() {
  const [transcriptions, setTranscriptions] = useState(mockTranscriptions);
  const [selectedTranscription, setSelectedTranscription] = useState<Transcription | null>(null);
  const [activeTab, setActiveTab] = useState('transcriptions');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedText, setCopiedText] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    }
    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    };
  }, [isRecording]);

  const stats = {
    total: transcriptions.length,
    completed: transcriptions.filter((t) => t.status === 'completed').length,
    processing: transcriptions.filter((t) => t.status === 'processing').length,
    totalMinutes: Math.round(
      transcriptions.reduce((sum, t) => sum + t.duration, 0) / 60
    ),
  };

  const filteredTranscriptions = transcriptions.filter((t) =>
    t.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    setRecordingTime(0);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    // Add new transcription
    const newTranscription: Transcription = {
      id: Date.now().toString(),
      filename: `gravacao_${new Date().toISOString().slice(0, 10)}.wav`,
      duration: recordingTime,
      language: 'pt-BR',
      status: 'processing',
      createdAt: new Date().toISOString(),
      confidence: 0,
    };
    setTranscriptions((prev) => [newTranscription, ...prev]);
    setRecordingTime(0);

    // Simulate processing
    setTimeout(() => {
      setTranscriptions((prev) =>
        prev.map((t) =>
          t.id === newTranscription.id
            ? {
                ...t,
                status: 'completed' as const,
                confidence: 95,
                text: 'Transcrição do áudio gravado...',
                completedAt: new Date().toISOString(),
              }
            : t
        )
      );
    }, 5000);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Mic className="w-8 h-8 text-accent-primary" />
              Reconhecimento de Voz
            </h1>
            <p className="text-text-secondary mt-1">
              Transcrição automática de áudio com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Upload className="w-4 h-4" />}
              onClick={() => setUploadModalOpen(true)}
            >
              Upload Áudio
            </Button>
          </div>
        </div>

        {/* Recording Widget */}
        <Card>
          <CardBody>
            <div className="flex items-center justify-center gap-8 py-6">
              <div className="text-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={isRecording ? handleStopRecording : handleStartRecording}
                  className={`w-24 h-24 rounded-full flex items-center justify-center transition-colors ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-accent-primary hover:bg-accent-primary/90'
                  }`}
                >
                  {isRecording ? (
                    <Square className="w-10 h-10 text-white" />
                  ) : (
                    <Mic className="w-10 h-10 text-white" />
                  )}
                </motion.button>
                <p className="mt-4 text-text-primary font-medium">
                  {isRecording ? 'Gravando...' : 'Clique para gravar'}
                </p>
              </div>

              {isRecording && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-6"
                >
                  {/* Waveform Animation */}
                  <div className="flex items-center gap-1 h-16">
                    {[...Array(20)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-1 bg-accent-primary rounded-full"
                        animate={{
                          height: [20, Math.random() * 60 + 20, 20],
                        }}
                        transition={{
                          duration: 0.5,
                          repeat: Infinity,
                          delay: i * 0.05,
                        }}
                      />
                    ))}
                  </div>

                  {/* Timer */}
                  <div className="text-center">
                    <p className="text-4xl font-mono font-bold text-red-500">
                      {formatDuration(recordingTime)}
                    </p>
                    <p className="text-sm text-text-muted">Duração</p>
                  </div>
                </motion.div>
              )}
            </div>
          </CardBody>
        </Card>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Arquivos"
              value={stats.total}
              icon={<FileAudio className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Transcritos"
              value={stats.completed}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Em Processamento"
              value={stats.processing}
              icon={<RefreshCw className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Minutos Transcritos"
              value={stats.totalMinutes}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="transcriptions" label="Transcrições" />
          <Tab value="speakers" label="Identificação de Falantes" />
          <Tab value="settings" label="Configurações" />
        </Tabs>

        {activeTab === 'transcriptions' && (
          <>
            {/* Search */}
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <Input
                      placeholder="Buscar transcrições..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                    Filtros
                  </Button>
                </div>
              </CardBody>
            </Card>

            {/* Transcriptions List */}
            <div className="space-y-4">
              {filteredTranscriptions.map((transcription) => {
                const StatusIcon = statusConfig[transcription.status].icon;
                return (
                  <Card key={transcription.id} className="hover:border-accent-primary/50 transition-colors">
                    <CardBody>
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                            <FileAudio className="w-6 h-6 text-accent-primary" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-medium text-text-primary">{transcription.filename}</h3>
                              <Badge variant={statusConfig[transcription.status].color}>
                                <StatusIcon
                                  className={`w-3 h-3 mr-1 ${
                                    transcription.status === 'processing' ? 'animate-spin' : ''
                                  }`}
                                />
                                {statusConfig[transcription.status].label}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-text-muted">
                              <span className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {formatDuration(transcription.duration)}
                              </span>
                              <span className="flex items-center gap-1">
                                <Languages className="w-4 h-4" />
                                {supportedLanguages.find((l) => l.code === transcription.language)?.name}
                              </span>
                              {transcription.status === 'completed' && (
                                <span className="flex items-center gap-1">
                                  <Sparkles className="w-4 h-4" />
                                  {transcription.confidence}% confiança
                                </span>
                              )}
                            </div>
                            {transcription.text && (
                              <p className="text-sm text-text-secondary mt-2 line-clamp-2">
                                {transcription.text}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {transcription.status === 'completed' && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsPlaying(!isPlaying)}
                              >
                                {isPlaying ? (
                                  <Pause className="w-4 h-4" />
                                ) : (
                                  <Play className="w-4 h-4" />
                                )}
                              </Button>
                              <Button
                                variant="secondary"
                                size="sm"
                                leftIcon={<Eye className="w-4 h-4" />}
                                onClick={() => {
                                  setSelectedTranscription(transcription);
                                  setDetailsModalOpen(true);
                                }}
                              >
                                Ver
                              </Button>
                            </>
                          )}
                          <Dropdown
                            trigger={
                              <Button variant="ghost" size="sm">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            }
                            items={[
                              { label: 'Download Áudio', icon: <Download className="w-4 h-4" /> },
                              { label: 'Download Transcrição', icon: <FileAudio className="w-4 h-4" /> },
                              { label: 'Reprocessar', icon: <RefreshCw className="w-4 h-4" /> },
                              { label: 'Excluir', icon: <Trash2 className="w-4 h-4" /> },
                            ]}
                          />
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                );
              })}
            </div>
          </>
        )}

        {activeTab === 'speakers' && (
          <Card>
            <CardHeader title="Identificação de Falantes" />
            <CardBody>
              <p className="text-text-muted mb-4">
                Configure a identificação automática de falantes nas transcrições.
              </p>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                  <div>
                    <p className="font-medium text-text-primary">Detecção automática de falantes</p>
                    <p className="text-sm text-text-muted">Identificar diferentes vozes automaticamente</p>
                  </div>
                  <input type="checkbox" defaultChecked className="toggle" />
                </div>
                <div className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                  <div>
                    <p className="font-medium text-text-primary">Número máximo de falantes</p>
                    <p className="text-sm text-text-muted">Limite de falantes a identificar</p>
                  </div>
                  <select className="px-3 py-2 bg-bg-secondary border border-border rounded-lg text-text-primary">
                    <option>2</option>
                    <option>4</option>
                    <option>6</option>
                    <option>8</option>
                    <option>Automático</option>
                  </select>
                </div>
                <div className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                  <div>
                    <p className="font-medium text-text-primary">Nomear falantes conhecidos</p>
                    <p className="text-sm text-text-muted">Associar nomes a vozes conhecidas</p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Configurar
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'settings' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Configurações de Transcrição" />
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-text-primary">Idioma padrão</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      {supportedLanguages.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">Qualidade de processamento</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Alta (mais preciso, mais lento)</option>
                      <option>Média (balanceado)</option>
                      <option>Rápida (menos preciso)</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Pontuação automática</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Detecção de idioma</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Filtrar palavras ofensivas</span>
                    <input type="checkbox" className="toggle" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Uso e Limites" />
              <CardBody>
                <div className="space-y-4">
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-text-muted">Minutos utilizados este mês</span>
                      <span className="font-medium text-text-primary">450 / 1000</span>
                    </div>
                    <Progress value={45} color="primary" />
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Arquivos processados este mês</p>
                    <p className="text-2xl font-bold text-text-primary">24</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Precisão média</p>
                    <p className="text-2xl font-bold text-green-500">95.3%</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Tempo médio de processamento</p>
                    <p className="text-2xl font-bold text-text-primary">1.5x</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload de Áudio"
        size="md"
      >
        <div className="space-y-4">
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent-primary transition-colors cursor-pointer">
            <Upload className="w-12 h-12 text-text-muted mx-auto mb-4" />
            <p className="text-text-primary font-medium">Arraste arquivos aqui</p>
            <p className="text-sm text-text-muted mt-1">ou clique para selecionar</p>
            <p className="text-xs text-text-muted mt-2">MP3, WAV, M4A, FLAC (máx. 500MB)</p>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Idioma do áudio</label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              <option value="">Detectar automaticamente</option>
              {supportedLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="speakers" className="rounded" />
            <label htmlFor="speakers" className="text-sm text-text-primary">
              Identificar falantes
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setUploadModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>
              Transcrever
            </Button>
          </div>
        </div>
      </Modal>

      {/* Details Modal */}
      <Modal
        isOpen={detailsModalOpen}
        onClose={() => setDetailsModalOpen(false)}
        title="Transcrição"
        size="lg"
      >
        {selectedTranscription && (
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center gap-4">
                <FileAudio className="w-8 h-8 text-accent-primary" />
                <div>
                  <p className="font-medium text-text-primary">{selectedTranscription.filename}</p>
                  <p className="text-sm text-text-muted">
                    {formatDuration(selectedTranscription.duration)} •{' '}
                    {supportedLanguages.find((l) => l.code === selectedTranscription.language)?.name}
                  </p>
                </div>
              </div>
              <Badge variant="success">{selectedTranscription.confidence}% confiança</Badge>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-text-primary">Texto Transcrito</h4>
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={copiedText ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  onClick={() => handleCopyText(selectedTranscription.text || '')}
                >
                  {copiedText ? 'Copiado!' : 'Copiar'}
                </Button>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg max-h-[300px] overflow-y-auto">
                <p className="text-text-secondary whitespace-pre-wrap">
                  {selectedTranscription.text}
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Download TXT
              </Button>
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Download SRT
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default VoiceRecognitionPage;
