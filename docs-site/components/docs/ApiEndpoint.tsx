interface ApiEndpointProps {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description?: string;
}

const methodColors = {
  GET: 'bg-blue-100 text-blue-700 border-blue-200',
  POST: 'bg-green-100 text-green-700 border-green-200',
  PUT: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  DELETE: 'bg-red-100 text-red-700 border-red-200',
  PATCH: 'bg-purple-100 text-purple-700 border-purple-200',
};

export default function ApiEndpoint({
  method,
  path,
  description,
}: ApiEndpointProps) {
  return (
    <div className="my-6 p-4 bg-gray-50 border border-gray-200 rounded-xl">
      <div className="flex items-center gap-3 mb-2">
        <span
          className={`px-3 py-1 text-xs font-bold uppercase rounded-lg border ${methodColors[method]}`}
        >
          {method}
        </span>
        <code className="text-sm font-mono text-gray-900 bg-white px-3 py-1 rounded-lg border border-gray-200">
          {path}
        </code>
      </div>
      {description && (
        <p className="text-sm text-gray-600 mt-2">{description}</p>
      )}
    </div>
  );
}
