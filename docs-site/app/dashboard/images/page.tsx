'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { UserImage } from '@/types/dashboard';
import ImageComparison from '@/components/dashboard/ImageComparison';
import { Image as ImageIcon, AlertCircle } from 'lucide-react';

export default function ImagesPage() {
  const [images, setImages] = useState<UserImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadImages();
  }, []);

  const loadImages = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDashboardImages();
      setImages(data);
    } catch (err) {
      setError('이미지를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
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
          onClick={loadImages}
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
          <h1 className="text-3xl font-bold text-gray-900">이미지 갤러리</h1>
          <p className="text-gray-600 mt-2">
            업로드한 이미지의 원본과 전처리 결과를 확인하세요
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-lg">
          <ImageIcon className="w-5 h-5 text-primary-600" />
          <span className="font-semibold text-primary-900">
            총 {images.length}개
          </span>
        </div>
      </div>

      {/* 이미지 그리드 */}
      {images.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl border border-gray-200">
          <ImageIcon className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-gray-600 text-lg">업로드한 이미지가 없습니다</p>
          <p className="text-gray-500 text-sm mt-2">
            지도를 업로드하여 AI 길찾기를 시작해보세요
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {images.map((image) => (
            <ImageComparison key={image.id} image={image} />
          ))}
        </div>
      )}
    </div>
  );
}
