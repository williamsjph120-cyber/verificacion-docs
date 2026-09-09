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
  const [previewSerial, setPreviewSerial] = useState('');
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    document_type: 'Diploma',
    holder_name: '',
    holder_id: '',
    organization: 'unicaribe',
  });

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    if (showUpload && formData.organization) {
      loadPreviewSerial();
    }
  }, [showUpload, formData.organization, formData.holder_name]);

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

  const loadPreviewSerial = async () => {
    try {
      const res = await documentsAPI.previewSerial(formData.organization, formData.holder_name || 'Titular');
      setPreviewSerial(res.data.serial);
    } catch (err) {
      console.error('Error al obtener serial');
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
      fd.append('description', formData.description);
      fd.append('document_type', formData.document_type);
      fd.append('holder_name', formData.holder_name);
      fd.append('holder_id', formData.holder_id);
      fd.append('organization', formData.organization);

      await documentsAPI.create(fd);
      toast.success('Documento subido exitosamente');
      setShowUpload(false);
      setFormData({ title: '', description: '', document_type: 'Diploma', holder_name: '', holder_id: '', organization: 'unicaribe' });
      fileInputRef.current.value = '';
      loadDocuments();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al subir documento');
    } finally {
      setUploading(false);
    }
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
    const url = `${window.location.origin}/app/${doc.organization}/${doc.serial}`;
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
            onClick={() => setShowUpload(!showUpload)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Subir Documento
          </button>
        </div>

        {showUpload && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-4">Nuevo Documento</h3>

            {previewSerial && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-600">Serial que se generará:</p>
                <p className="text-2xl font-mono font-bold text-blue-800">{previewSerial}</p>
              </div>
            )}

            <form onSubmit={handleUpload} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organización *</label>
                  <select
                    value={formData.organization}
                    onChange={(e) => setFormData({...formData, organization: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                    required
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">ID del Titular</label>
                  <input
                    type="text"
                    value={formData.holder_id}
                    onChange={(e) => setFormData({...formData, holder_id: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                    rows="2"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Archivo PDF *</label>
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept=".pdf"
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={uploading}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {uploading ? 'Subiendo...' : 'Subir Documento'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUpload(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
              </div>
            </form>
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
                    to={`/app/${doc.organization}/${doc.serial}`}
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
