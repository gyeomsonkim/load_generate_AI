'use client';

import { useState } from 'react';
import Image from 'next/image';
import { UserImage } from '@/types/dashboard';

interface ImageComparisonProps {
  image: UserImage;
}

export default function ImageComparison({ image }: ImageComparisonProps) {
  const [activeTab, setActiveTab] = useState<'original' | 'processed'>('original');

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
      {/* 이미지 헤더 */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">
          {image.map?.name || `지도 #${image.map_id}`}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {new Date(image.upload_timestamp).toLocaleString('ko-KR')}
        </p>
      </div>

      {/* 탭 */}
      <div className="flex border-b border-gray-200 bg-gray-50">
        <button
          onClick={() => setActiveTab('original')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'original'
              ? 'bg-white text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          원본 이미지
        </button>
        <button
          onClick={() => setActiveTab('processed')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'processed'
              ? 'bg-white text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          전처리 이미지
        </button>
      </div>

      {/* 이미지 표시 */}
      <div className="relative aspect-video bg-gray-100">
        {image.map?.original_image_url && activeTab === 'original' ? (
          <Image
            src={image.map.original_image_url}
            alt={`${image.map.name} - 원본`}
            fill
            className="object-contain"
          />
        ) : image.map?.processed_image_url && activeTab === 'processed' ? (
          <Image
            src={image.map.processed_image_url}
            alt={`${image.map.name} - 전처리`}
            fill
            className="object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            이미지 없음
          </div>
        )}
      </div>

      {/* 이미지 정보 */}
      <div className="p-4 bg-gray-50">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">지도 타입</p>
            <p className="font-medium text-gray-900">
              {image.map?.map_type || 'Unknown'}
            </p>
          </div>
          <div>
            <p className="text-gray-600">처리 상태</p>
            <p className="font-medium text-gray-900">
              {image.map?.processing_status === 'completed'
                ? '완료'
                : image.map?.processing_status === 'processing'
                ? '처리 중'
                : '대기 중'}
            </p>
          </div>
          {image.map?.image_width && image.map?.image_height && (
            <>
              <div>
                <p className="text-gray-600">해상도</p>
                <p className="font-medium text-gray-900">
                  {image.map.image_width} × {image.map.image_height}
                </p>
              </div>
              <div>
                <p className="text-gray-600">파일 크기</p>
                <p className="font-medium text-gray-900">
                  {image.map.file_size
                    ? `${(image.map.file_size / 1024 / 1024).toFixed(2)} MB`
                    : 'Unknown'}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
