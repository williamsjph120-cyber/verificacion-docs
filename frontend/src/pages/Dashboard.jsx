import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { documentsAPI } from '../services/api';
import toast from 'react-hot-toast';

const ORGANIZATIONS = [
  { value: 'unicaribe', label: 'Universidad del Caribe' },
];

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState(1);
  const [previewData, setPreviewData] = useState(null);
  const [generating, setGenerating] = useState(false);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    title: '',
    document_type: 'Diploma',
    holder_name: '',
    issue_date: '',
    organization: 'unicaribe',
  });

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const res = await documentsAPI.list();
      setDocuments(res.data);
    } catch (err) {
      toast.error('Error al cargar documentos');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQR = async () => {
    if (!formData.holder_name || !formData.title) {
      toast.error('Llena el nombre del titular y el título primero');
      return;
    }
    setGenerating(true);
    try {
      const res = await documentsAPI.previewQR(formData.organization, formData.holder_name);
      setPreviewData(res.data);
      setStep(2);
    } catch (err) {
      toast.error('Error al generar serial y QR');
    } finally {
      setGenerating(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const file = fileInputRef.current?.files[0];
    if (!file) {
      toast.error('Seleccione un archivo PDF');
      return;
    }

    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('title', formData.title);
      fd.append('document_type', formData.document_type);
      fd.append('holder_name', formData.holder_name);
      fd.append('issue_date', formData.issue_date);
      fd.append('organization', formData.organization);

      await documentsAPI.create(fd);
      toast.success('Documento subido exitosamente');
      resetForm();
      loadDocuments();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al subir documento');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setShowUpload(false);
    setStep(1);
    setPreviewData(null);
    setFormData({ title: '', document_type: 'Diploma', holder_name: '', issue_date: '', organization: 'unicaribe' });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar este documento?')) return;
    try {
      await documentsAPI.delete(id);
      toast.success('Documento eliminado');
      loadDocuments();
    } catch (err) {
      toast.error('Error al eliminar');
    }
  };

  const copyVerifyLink = (doc) => {
    const url = `${window.location.origin}/inbox/app/${doc.organization}/${doc.serial}`;
    navigator.clipboard.writeText(url);
    toast.success('Enlace copiado');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">Verificación de Documentos</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.full_name}</span>
            <button onClick={logout} className="text-sm text-red-600 hover:text-red-800">Salir</button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-700">Mis Documentos</h2>
          <button
            onClick={() => { setShowUpload(!showUpload); setStep(1); setPreviewData(null); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Subir Documento
          </button>
        </div>

        {showUpload && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-4">
              {step === 1 ? 'Paso 1: Datos del Documento' : 'Paso 2: Subir PDF'}
            </h3>

            {step === 1 && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Organización *</label>
                    <select
                      value={formData.organization}
                      onChange={(e) => setFormData({...formData, organization: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                    >
                      {ORGANIZATIONS.map((org) => (
                        <option key={org.value} value={org.value}>{org.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento *</label>
                    <select
                      value={formData.document_type}
                      onChange={(e) => setFormData({...formData, document_type: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                    >
                      <option>Diploma</option>
                      <option>Certificado</option>
                      <option>Cédula</option>
                      <option>Constancia</option>
                      <option>Otro</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Título *</label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Titular *</label>
                    <input
                      type="text"
                      value={formData.holder_name}
                      onChange={(e) => setFormData({...formData, holder_name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Expedición *</label>
                    <input
                      type="date"
                      value={formData.issue_date}
                      onChange={(e) => setFormData({...formData, issue_date: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleGenerateQR}
                    disabled={generating}
                    className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
                  >
                    {generating ? 'Generando...' : 'Generar Serial y QR'}
                  </button>
                  <button
                    type="button"
                    onClick={resetForm}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            {step === 2 && previewData && (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-600 mb-1">Serial generado:</p>
                  <p className="text-2xl font-mono font-bold text-green-800 mb-2">{previewData.serial}</p>
                  <p className="text-sm text-green-600">URL de verificación:</p>
                  <p className="text-sm font-mono text-green-700 break-all">{previewData.verify_url}</p>
                </div>

                <div className="flex flex-col items-center bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Código QR generado:</p>
                  <img src={previewData.qr_code_url} alt="QR Code" className="w-48 h-48 border-2 border-gray-200 rounded-lg" />
                  <p className="text-xs text-gray-500 mt-2">Imprime este QR y colócalo en el documento físico</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Archivo PDF del documento *</label>
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept=".pdf"
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleUpload}
                    disabled={uploading}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                  >
                    {uploading ? 'Subiendo...' : 'Subir Documento'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="bg-yellow-500 text-white px-4 py-2 rounded-md hover:bg-yellow-600"
                  >
                    ← Volver
                  </button>
                  <button
                    type="button"
                    onClick={resetForm}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {loading ? (
          <p className="text-gray-500">Cargando...</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No hay documentos. Sube el primero.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-white p-4 rounded-lg shadow-md">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{doc.document_type}</span>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Eliminar
                  </button>
                </div>
                <h3 className="font-semibold text-gray-800 mb-1">{doc.title}</h3>
                <p className="text-sm text-gray-600 mb-1">{doc.holder_name}</p>
                <p className="text-xs text-gray-500 mb-1">{doc.organization}</p>
                <p className="font-mono text-sm font-bold text-blue-600 mb-3">{doc.serial}</p>
                <div className="flex gap-2 flex-wrap">
                  <Link
                    to={`/documentos/${doc.id}`}
                    className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded text-gray-700"
                  >
                    Ver QR
                  </Link>
                  <button
                    onClick={() => copyVerifyLink(doc)}
                    className="text-sm bg-green-100 hover:bg-green-200 px-3 py-1 rounded text-green-700"
                  >
                    Copiar Link
                  </button>
                  <Link
                    to={`/inbox/app/${doc.organization}/${doc.serial}`}
                    target="_blank"
                    className="text-sm bg-blue-100 hover:bg-blue-200 px-3 py-1 rounded text-blue-700"
                  >
                    Verificar
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
