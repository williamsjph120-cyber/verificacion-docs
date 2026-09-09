import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { documentsAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocument();
  }, [id]);

  const loadDocument = async () => {
    try {
      const res = await documentsAPI.get(id);
      setDoc(res.data);
    } catch (err) {
      toast.error('Error al cargar documento');
    } finally {
      setLoading(false);
    }
  };

  const copyVerifyLink = () => {
    const url = `${window.location.origin}/ibox/app/${doc.organization}/${doc.serial}`;
    navigator.clipboard.writeText(url);
    toast.success('Enlace copiado');
  };

  const downloadQR = () => {
    if (doc.qr_code_url) {
      const link = document.createElement('a');
      link.href = doc.qr_code_url;
      link.download = `QR-${doc.serial}.png`;
      link.click();
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!doc) return <div className="min-h-screen flex items-center justify-center">Documento no encontrado</div>;

  const verifyUrl = `${window.location.origin}/ibox/app/${doc.organization}/${doc.serial}`;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <Link to="/dashboard" className="text-blue-600 hover:text-blue-800">← Volver</Link>
          <h1 className="text-xl font-bold text-gray-800">{doc.title}</h1>
          <div></div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-lg font-semibold mb-4">Información del Documento</h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">Serial:</span>
                <p className="font-mono text-2xl font-bold text-blue-600">{doc.serial}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Organización:</span>
                <p className="font-medium">{doc.organization}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Título:</span>
                <p className="font-medium">{doc.title}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Tipo:</span>
                <p className="font-medium">{doc.document_type}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Titular:</span>
                <p className="font-medium">{doc.holder_name}</p>
              </div>
              {doc.holder_id && (
                <div>
                  <span className="text-sm text-gray-500">ID:</span>
                  <p className="font-medium">{doc.holder_id}</p>
                </div>
              )}
              {doc.description && (
                <div>
                  <span className="text-sm text-gray-500">Descripción:</span>
                  <p className="font-medium">{doc.description}</p>
                </div>
              )}
              <div>
                <span className="text-sm text-gray-500">URL de verificación:</span>
                <p className="font-mono text-sm bg-gray-100 p-2 rounded break-all">
                  {verifyUrl}
                </p>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={copyVerifyLink}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
              >
                Copiar Enlace
              </button>
              <Link
                to={`/ibox/app/${doc.organization}/${doc.serial}`}
                target="_blank"
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
              >
                Probar Verificación
              </Link>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md flex flex-col items-center">
            <h2 className="text-lg font-semibold mb-4">Código QR</h2>
            {doc.qr_code_url ? (
              <>
                <img
                  src={doc.qr_code_url}
                  alt="QR Code"
                  className="w-64 h-64 border-2 border-gray-200 rounded-lg"
                />
                <p className="mt-2 font-mono text-sm font-bold text-center">{doc.serial}</p>
                <button
                  onClick={downloadQR}
                  className="mt-4 bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm"
                >
                  Descargar QR
                </button>
                <p className="mt-2 text-xs text-gray-500 text-center">
                  Imprima este código QR y colóquelo en el documento físico
                </p>
              </>
            ) : (
              <p className="text-gray-500">QR no disponible</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
