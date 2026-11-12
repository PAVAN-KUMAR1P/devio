import React, { useState, useEffect } from 'react';
import { ClusterSummaryEntry, ClusterDetail } from '../types/api';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { Badge } from '../components/common/Badge';
import { Boxes, Network, Award, Compass, CheckCircle2 } from 'lucide-react';

interface ClustersPageProps {
  onSelectDistrict: (id: string) => void;
  onNavigatePage: (page: any) => void;
}

export const ClustersPage: React.FC<ClustersPageProps> = ({
  onSelectDistrict,
  onNavigatePage,
}) => {
  const [clusters, setClusters] = useState<ClusterSummaryEntry[]>([]);
  const [activeCluster, setActiveCluster] = useState<number>(0);
  const [clusterDistricts, setClusterDistricts] = useState<ClusterDetail[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadClusters() {
      setLoading(true);
      setError(null);
      try {
        const cData = await api.getClusters();
        if (isMounted) {
          setClusters(cData);
          if (cData.length > 0) {
            setActiveCluster(cData[0].cluster_label);
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load clusters');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadClusters();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    async function loadDistricts() {
      try {
        const dData = await api.getClusterDistricts(activeCluster);
        if (isMounted) setClusterDistricts(dData);
      } catch (err: any) {
        console.error('Error loading cluster districts:', err);
      }
    }
    loadDistricts();
    return () => {
      isMounted = false;
    };
  }, [activeCluster]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-2">
          <Boxes className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">
            Unsupervised Machine Learning: K-Means & Hierarchical Clustering
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Districts grouped into 3 distinct developmental typologies using 14 standardized indicators (StandardScaler, k=3, Ward Linkage)
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading cluster data..." />
      ) : error ? (
        <ErrorAlert message={error} />
      ) : (
        <>
          {/* Cluster Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {clusters.map((c) => {
              const isSelected = activeCluster === c.cluster_label;
              return (
                <div
                  key={c.cluster_label}
                  onClick={() => setActiveCluster(c.cluster_label)}
                  className={`p-5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-600/15 border-blue-500 shadow-lg shadow-blue-500/10'
                      : 'bg-slate-800/80 border-slate-700/80 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-slate-400">Cluster {c.cluster_label}</span>
                    <Badge variant={isSelected ? 'primary' : 'slate'}>
                      {c.district_count} Districts
                    </Badge>
                  </div>
                  <h3 className="mt-2 text-base font-bold text-white">{c.cluster_name}</h3>
                  <div className="mt-4 pt-3 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                    <span>Avg Centroid Dist:</span>
                    <span className="font-mono font-semibold text-slate-200">
                      {c.avg_centroid_dist?.toFixed(3) || 'N/A'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active Cluster Details & Member Districts */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700/60">
              <div>
                <h3 className="text-sm font-semibold text-white">
                  Member Districts in Cluster {activeCluster} (
                  {clusters.find((c) => c.cluster_label === activeCluster)?.cluster_name})
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Ordered by composite overall development score
                </p>
              </div>
              <span className="text-xs text-blue-400 font-semibold font-mono">
                {clusterDistricts.length} Districts
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {clusterDistricts.map((d) => (
                <div
                  key={d.district_id}
                  onClick={() => {
                    onSelectDistrict(d.district_id);
                    onNavigatePage('district');
                  }}
                  className="p-3 bg-slate-900/60 border border-slate-700/50 hover:border-blue-500/50 rounded-lg cursor-pointer transition-all flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-xs font-bold text-white hover:text-blue-400">
                      {d.district_name}
                    </h4>
                    <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                      Centroid Dist: {d.distance_to_centroid?.toFixed(3) || 'N/A'}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {d.overall_score?.toFixed(1) || 'N/A'}
                    </span>
                    <span className="text-[10px] text-slate-400 block">/ 100</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hierarchical Clustering / Ward Linkage Insights Card */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 shadow-lg">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-700/60 mb-3">
              <Network className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Hierarchical Dendrogram Analysis</h3>
            </div>
            <div className="text-xs text-slate-300 space-y-2 leading-relaxed">
              <p>
                • <strong>Methodology:</strong> Agglomerative clustering executed using Euclidean distance and Ward's minimum variance criterion, which minimizes within-cluster variance at each step.
              </p>
              <p>
                • <strong>Diagnostic Cut:</strong> Cutting the tree at $k=3$ produced a silhouette coefficient of <strong>0.1104</strong>, corroborating the K-Means partition ($0.1097$).
              </p>
              <p>
                • <strong>Structural Insight:</strong> The urban innovation core (Bengaluru Urban) forms a discrete isolated branch due to its extreme positive skew in patent applications (18.4 vs state mean 1.8) and DPIIT startups (108.3 vs state mean 5.2).
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
