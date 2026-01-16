import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Download,
  RotateCw,
  Maximize,
  ChevronLeft,
  FileText,
  Eye
} from 'lucide-react';
import type { Document, OCRResult } from '../types';

interface PDFViewerProps {
  document: Document;
  ocrResult?: OCRResult;
  onClose?: () => void;
  onDownload?: () => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  document,
  ocrResult,
  onClose,
  onDownload,
}) => {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [showOCR, setShowOCR] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 25, 300));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);

  const isPDF = document.type.toLowerCase() === 'pdf';
  const isImage = ['jpg', 'jpeg', 'png', 'gif'].includes(document.type.toLowerCase());

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 ${fullscreen ? 'p-0' : 'p-4'}`}>
      <div className={`bg-white rounded-lg shadow-xl flex flex-col ${fullscreen ? 'w-full h-full rounded-none' : 'w-full max-w-6xl h-full max-h-[90vh]'}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <FileText className="w-5 h-5 text-gray-500" />
            <div>
              <h3 className="text-lg font-medium text-gray-900">{document.name}</h3>
              <p className="text-sm text-gray-500">
                {document.type.toUpperCase()} • Versão {document.version}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* OCR Toggle */}
            {ocrResult && (
              <button
                onClick={() => setShowOCR(!showOCR)}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  showOCR 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-700'
                } hover:bg-blue-200`}
              >
                <Eye className="w-4 h-4 inline mr-1" />
                OCR {showOCR ? 'ON' : 'OFF'}
              </button>
            )}

            {/* Zoom Controls */}
            <div className="flex items-center space-x-1 bg-gray-100 rounded p-1">
              <button
                onClick={handleZoomOut}
                className="p-1 text-gray-600 hover:text-gray-900"
                disabled={zoom <= 50}
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="px-2 py-1 text-sm font-medium text-gray-700 min-w-[60px] text-center">
                {zoom}%
              </span>
              <button
                onClick={handleZoomIn}
                className="p-1 text-gray-600 hover:text-gray-900"
                disabled={zoom >= 300}
              >
                <ZoomIn className="w-4 h-4" />
              </button>
            </div>

            {/* Rotate */}
            <button
              onClick={handleRotate}
              className="p-2 text-gray-600 hover:text-gray-900"
              title="Girar"
            >
              <RotateCw className="w-4 h-4" />
            </button>

            {/* Fullscreen */}
            <button
              onClick={() => setFullscreen(!fullscreen)}
              className="p-2 text-gray-600 hover:text-gray-900"
              title="Tela cheia"
            >
              <Maximize className="w-4 h-4" />
            </button>

            {/* Download */}
            {onDownload && (
              <button
                onClick={onDownload}
                className="p-2 text-gray-600 hover:text-gray-900"
                title="Download"
              >
                <Download className="w-4 h-4" />
              </button>
            )}

            {/* Close */}
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 text-gray-600 hover:text-gray-900"
                title="Fechar"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 relative overflow-hidden bg-gray-100">
          <div className="absolute inset-0 overflow-auto p-4">
            <div className="flex justify-center">
              
              {/* PDF Viewer */}
              {isPDF && (
                <div 
                  className="bg-white shadow-lg"
                  style={{ 
                    transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                    transformOrigin: 'top center'
                  }}
                >
                  <iframe
                    src={`${document.url}#view=FitH`}
                    className="w-[595px] h-[842px] border-0" // A4 size
                    title={document.name}
                  />
                </div>
              )}

              {/* Image Viewer */}
              {isImage && (
                <div className="relative">
                  <img
                    src={document.url}
                    alt={document.name}
                    className="max-w-none bg-white shadow-lg"
                    style={{ 
                      transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                      transformOrigin: 'center'
                    }}
                  />
                  
                  {/* OCR Overlay */}
                  {showOCR && ocrResult?.boundingBoxes && (
                    <div className="absolute inset-0 pointer-events-none">
                      {ocrResult.boundingBoxes.map((box, index) => (
                        <div
                          key={index}
                          className="absolute border border-blue-500 bg-blue-100 bg-opacity-30"
                          style={{
                            left: `${box.x}px`,
                            top: `${box.y}px`,
                            width: `${box.width}px`,
                            height: `${box.height}px`,
                            transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                          }}
                          title={box.text}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Other File Types */}
              {!isPDF && !isImage && (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                  <FileText className="w-16 h-16 mb-4" />
                  <p className="text-lg font-medium">Visualização não disponível</p>
                  <p className="text-sm">Tipo de arquivo: {document.type.toUpperCase()}</p>
                  {onDownload && (
                    <button
                      onClick={onDownload}
                      className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      <Download className="w-4 h-4 inline mr-2" />
                      Download para visualizar
                    </button>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>

        {/* OCR Text Panel */}
        {showOCR && ocrResult && (
          <div className="border-t border-gray-200 bg-gray-50 p-4 max-h-48 overflow-y-auto">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Texto Extraído (OCR - {Math.round(ocrResult.confidence * 100)}% confiança)
            </h4>
            <div className="text-sm text-gray-700 whitespace-pre-wrap bg-white p-3 rounded border">
              {ocrResult.text || 'Nenhum texto detectado'}
            </div>
          </div>
        )}

        {/* Footer with document info */}
        <div className="border-t border-gray-200 px-4 py-3 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              Categoria: {document.category} • Tags: {document.tags.join(', ')}
            </div>
            <div>
              Enviado por {document.uploadedBy} em {new Date(document.uploadDate).toLocaleDateString('pt-BR')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
