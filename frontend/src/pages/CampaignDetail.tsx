import React from 'react';
import { useParams } from 'react-router-dom';

export function CampaignDetail() {
  const { id } = useParams();
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Campaign Detail</h1>
      <p>Campaign ID: {id}</p>
      <div className="card p-6">
        <p className="text-gray-600">Campaign detail page coming soon...</p>
      </div>
    </div>
  );
}
