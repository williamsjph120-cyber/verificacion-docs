import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { verifyAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function Verify() {
  const { org, serial } = useParams();
  const [captcha, setCaptcha] = useState(null);
  const [captchaText, setCaptchaText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [captchaLoading, setCaptchaLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCaptcha();
  }, [org, serial]);

  const loadCaptcha = async () => {
    setCaptchaLoading(true);
    setError(null);
    try {
      const res = await verifyAPI.getCaptcha(org, serial);
      setCaptcha(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar verificación');
    } finally {
      setCaptchaLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!captchaText.trim()) {
      toast.error('Ingrese el código de seguridad');
      return;
    }

    setLoading(true);
    try {
      const res = await verifyAPI.verify(org, serial, captchaText);
      setResult(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al verificar');
      loadCaptcha();
      setCaptchaText('');
    } finally {
      setLoading(false);
    }
  };

  if (captchaLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando verificación...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-3xl w-full mx-4">
          <div className="text-center mb-6">
            <div className="text-green-500 text-5xl mb-4">✓</div>
            <h2 className="text-2xl font-bold text-gray-800">Documento Verificado</h2>
            <p className="text-gray-500 mt-2">{result.message}</p>
          </div>

          <div className="border-t pt-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-500">Serial:</span>
                <p className="font-mono font-bold text-lg">{result.document.serial}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Tipo:</span>
                <p className="font-medium">{result.document.document_type}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Título:</span>
                <p className="font-medium">{result.document.title}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Titular:</span>
                <p className="font-medium">{result.document.holder_name}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Organización:</span>
                <p className="font-medium">{result.document.organization}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Fecha de Verificación:</span>
                <p className="font-medium">{new Date(result.document.verified_at).toLocaleString('es-DO')}</p>
              </div>
            </div>
          </div>

          {result.document.file_url && (
            <div className="mt-6 border-t pt-6">
              <h3 className="text-lg font-semibold mb-3">Documento</h3>
              <iframe
                src={result.document.file_url}
                className="w-full border-2 border-gray-200 rounded-lg"
                style={{ height: '500px' }}
                title="Documento PDF"
              />
              <div className="mt-3 flex gap-2">
                <a
                  href={result.document.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                >
                  Abrir en nueva pestaña
                </a>
                <a
                  href={result.document.file_url}
                  download
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm"
                >
                  Descargar
                </a>
              </div>
            </div>
          )}

          <div className="mt-6 flex gap-3 justify-center">
            <button
              onClick={() => { setResult(null); setCaptchaText(''); loadCaptcha(); }}
              className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400"
            >
              Verificar Otro
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md mx-4">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">Verificación de Documento</h2>
          <p className="text-sm text-gray-500 mt-1">Ingrese el código de seguridad para verificar</p>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Serial del Documento
          </label>
          <input
            type="text"
            value={serial}
            readOnly
            className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-sm font-mono font-bold"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Organización
          </label>
          <input
            type="text"
            value={org}
            readOnly
            className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-sm"
          />
        </div>

        {captcha && (
          <div className="mb-4 text-center">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Escribe el código de seguridad
            </label>
            <img
              src={captcha.captcha_image}
              alt="CAPTCHA"
              className="mx-auto border-2 border-gray-300 rounded-lg mb-3"
            />
            <input
              type="text"
              value={captchaText}
              onChange={(e) => setCaptchaText(e.target.value)}
              placeholder="Escribe el código que ves arriba"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-center text-lg tracking-widest"
              maxLength={10}
              autoFocus
            />
          </div>
        )}

        <button
          onClick={handleVerify}
          disabled={loading || !captcha}
          className="w-full bg-cyan-500 text-white py-3 rounded-md hover:bg-cyan-600 disabled:opacity-50 font-semibold text-lg"
        >
          {loading ? 'Verificando...' : 'Verificar'}
        </button>

        <p className="text-xs text-gray-400 text-center mt-4">
          Sistema de Verificación de Documentos
        </p>
      </div>
    </div>
  );
}
