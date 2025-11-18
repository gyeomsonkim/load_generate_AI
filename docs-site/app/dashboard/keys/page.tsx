'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { ApiKeyInfo } from '@/types/auth';
import { maskApiKey } from '@/lib/utils/format';
import {
  Key,
  Plus,
  Trash2,
  Copy,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKeyInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getApiKeys();
      setKeys(data);
    } catch (err) {
      setError('API 키 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async () => {
    try {
      setCreating(true);
      const newKey = await apiClient.createApiKey();
      setKeys([newKey, ...keys]);
    } catch (err) {
      alert('API 키 생성에 실패했습니다.');
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteKey = async (keyId: number) => {
    if (!confirm('정말 이 API 키를 삭제하시겠습니까?')) return;

    try {
      await apiClient.deleteApiKey(keyId);
      setKeys(keys.filter((k) => k.id !== keyId));
    } catch (err) {
      alert('API 키 삭제에 실패했습니다.');
      console.error(err);
    }
  };

  const handleCopyKey = (key: string, id: number) => {
    navigator.clipboard.writeText(key);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-gray-600">{error}</p>
        <button
          onClick={loadKeys}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API 키 관리</h1>
          <p className="text-gray-600 mt-2">
            API 키를 생성하고 관리하세요
          </p>
        </div>
        <button
          onClick={handleCreateKey}
          disabled={creating}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>{creating ? '생성 중...' : '새 API 키'}</span>
        </button>
      </div>

      {/* API 키 목록 */}
      {keys.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl border border-gray-200">
          <Key className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-gray-600 text-lg">생성된 API 키가 없습니다</p>
          <p className="text-gray-500 text-sm mt-2">
            새 API 키를 생성하여 서비스를 시작하세요
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {keys.map((key) => (
            <div
              key={key.id}
              className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                {/* 키 정보 */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <Key className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-mono text-lg font-semibold text-gray-900">
                        {maskApiKey(key.key)}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        생성일: {new Date(key.created_at).toLocaleString('ko-KR')}
                      </p>
                    </div>
                  </div>

                  {/* 통계 */}
                  <div className="flex items-center gap-6 mt-4">
                    <div>
                      <p className="text-sm text-gray-600">사용 횟수</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {key.usage_count.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">상태</p>
                      <p
                        className={`text-lg font-semibold ${
                          key.is_active ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {key.is_active ? '활성' : '비활성'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 액션 버튼 */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopyKey(key.key, key.id)}
                    className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    title="복사"
                  >
                    {copiedId === key.id ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </button>
                  <button
                    onClick={() => handleDeleteKey(key.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="삭제"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 안내 사항 */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-2">💡 API 키 사용 안내</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• API 키는 6자리 숫자로 구성됩니다</li>
          <li>• 각 API 요청 시 X-API-Key 헤더에 키를 포함해야 합니다</li>
          <li>• API 키는 안전하게 보관하고 타인과 공유하지 마세요</li>
          <li>• 키가 유출된 경우 즉시 삭제하고 새로운 키를 생성하세요</li>
        </ul>
      </div>
    </div>
  );
}
