'use client';

import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

const codeExamples = {
  javascript: `// 지도 업로드
const formData = new FormData();
formData.append('file', mapImage);
formData.append('name', 'Central Park');
formData.append('map_type', 'park');

const response = await fetch('http://localhost:8000/api/v1/maps/upload', {
  method: 'POST',
  headers: {
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: formData
});

const data = await response.json();
console.log(data.map.id);

// 경로 찾기
const pathResponse = await fetch('http://localhost:8000/api/v1/pathfinding/route', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    map_id: data.map.id,
    start: { x: 10, y: 20 },
    end: { x: 100, y: 200 }
  })
});

const path = await pathResponse.json();
console.log('경로:', path.path);`,

  python: `# 지도 업로드
import requests

url = "http://localhost:8000/api/v1/maps/upload"
headers = {"X-API-Key": "YOUR_API_KEY"}

with open("map.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "name": "Central Park",
        "map_type": "park"
    }
    response = requests.post(url, headers=headers, files=files, data=data)

map_data = response.json()
map_id = map_data["map"]["id"]

# 경로 찾기
path_url = "http://localhost:8000/api/v1/pathfinding/route"
path_data = {
    "map_id": map_id,
    "start": {"x": 10, "y": 20},
    "end": {"x": 100, "y": 200}
}

path_response = requests.post(path_url, headers=headers, json=path_data)
path = path_response.json()
print("경로:", path["path"])`,
};

export default function APIPreview() {
  const [activeTab, setActiveTab] = useState<'javascript' | 'python'>('javascript');
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(codeExamples[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-24 px-4 bg-gray-900">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            간단한 API 사용
          </h2>
          <p className="text-xl text-gray-300">
            몇 줄의 코드로 AI 길찾기 기능을 바로 사용하세요
          </p>
        </div>

        {/* Code Preview */}
        <div className="bg-gray-950 rounded-2xl overflow-hidden shadow-2xl border border-gray-800">
          {/* Tabs */}
          <div className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('javascript')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'javascript'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                JavaScript
              </button>
              <button
                onClick={() => setActiveTab('python')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'python'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                Python
              </button>
            </div>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white transition-colors rounded-lg hover:bg-gray-800"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span className="text-sm">복사됨!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span className="text-sm">복사</span>
                </>
              )}
            </button>
          </div>

          {/* Code */}
          <div className="p-6 overflow-x-auto">
            <pre className="text-sm md:text-base">
              <code className="text-gray-100 font-mono leading-relaxed">
                {codeExamples[activeTab]}
              </code>
            </pre>
          </div>
        </div>

        {/* Features List */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="text-center">
            <div className="text-4xl mb-2">⚡</div>
            <h4 className="text-white font-semibold mb-2">빠른 응답</h4>
            <p className="text-gray-400 text-sm">평균 500ms 이내 응답</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">🔒</div>
            <h4 className="text-white font-semibold mb-2">안전한 API</h4>
            <p className="text-gray-400 text-sm">키 기반 간편 인증</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">📚</div>
            <h4 className="text-white font-semibold mb-2">풍부한 문서</h4>
            <p className="text-gray-400 text-sm">상세한 예제와 가이드</p>
          </div>
        </div>
      </div>
    </section>
  );
}
