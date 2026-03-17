'use client';

import { useState } from 'react';
import {
  Fingerprint,
  Camera,
  MapPin,
  CheckCircle2,
  Clock,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface PunchRecord {
  tipo: string;
  hora: string;
  local: string;
}

const lastPunches: PunchRecord[] = [
  { tipo: 'Entrada', hora: '08:02', local: 'Posto Central - Manaus' },
  { tipo: 'Saida Almoco', hora: '12:00', local: 'Posto Central - Manaus' },
  { tipo: 'Retorno Almoco', hora: '13:05', local: 'Posto Central - Manaus' },
];

export default function BaterPontoPage() {
  const [punching, setPunching] = useState(false);
  const [punched, setPunched] = useState(false);
  const [geoEnabled] = useState(true);
  const [currentTime] = useState(new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

  function handlePunch() {
    setPunching(true);
    setTimeout(() => {
      setPunching(false);
      setPunched(true);
      setTimeout(() => setPunched(false), 3000);
    }, 2000);
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-2">
        <Fingerprint className="w-6 h-6 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Bater Ponto</h1>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-8 flex flex-col items-center">
          <p className="text-5xl font-bold text-gray-900 mb-2">{currentTime}</p>
          <p className="text-sm text-gray-500 mb-8">
            {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}
          </p>

          <button
            onClick={handlePunch}
            disabled={punching}
            className={`w-40 h-40 rounded-full flex flex-col items-center justify-center gap-2 text-white font-bold text-lg transition-all duration-300 shadow-lg ${
              punched
                ? 'bg-green-500 scale-95'
                : punching
                ? 'bg-blue-400 animate-pulse scale-105'
                : 'bg-blue-600 hover:bg-blue-700 hover:scale-105 active:scale-95'
            }`}
          >
            {punched ? (
              <>
                <CheckCircle2 className="w-10 h-10" />
                <span className="text-sm">Registrado!</span>
              </>
            ) : (
              <>
                <Camera className="w-10 h-10" />
                <span className="text-sm">{punching ? 'Registrando...' : 'Bater Ponto'}</span>
              </>
            )}
          </button>

          <div className="mt-8 flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              {geoEnabled ? (
                <MapPin className="h-4 w-4 text-green-500" />
              ) : (
                <MapPin className="h-4 w-4 text-red-500" />
              )}
              <span className={geoEnabled ? 'text-green-600' : 'text-red-600'}>
                {geoEnabled ? 'GPS Ativo' : 'GPS Inativo'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Wifi className="h-4 w-4 text-green-500" />
              <span className="text-green-600">Online</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border border-gray-200">
        <CardContent className="p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Batidas de Hoje</h2>
          <div className="space-y-3">
            {lastPunches.map((punch, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{punch.tipo}</p>
                    <p className="text-xs text-gray-500">{punch.local}</p>
                  </div>
                </div>
                <span className="text-sm font-mono font-medium text-gray-700">{punch.hora}</span>
              </div>
            ))}
            <div className="flex items-center justify-between py-2 opacity-50">
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-gray-300" />
                <p className="text-sm text-gray-400">Saida — Aguardando</p>
              </div>
              <span className="text-sm text-gray-400">--:--</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
