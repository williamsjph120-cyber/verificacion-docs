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

  const getGoogleViewerUrl = (url) => {
    return `https://docs.google.com/gview?url=${encodeURIComponent(url)}&embedded=true`;
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
          <div className="text-red-500 text-5xl mb-4">&#9888;</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (result) {
    const fileUrl = result.document.file_url;
    return (
      <div className="min-h-screen bg-white">
        <iframe
          src={getGoogleViewerUrl(fileUrl)}
          className="w-full h-screen border-0"
          title="Documento PDF"
          allow="autoplay"
        />
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
          className="bg-cyan-400 hover:bg-cyan-500 text-white font-semibold py-2.5 px-6 rounded-md disabled:opacity-50 text-sm"
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
