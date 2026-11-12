import React, { useState, useEffect } from 'react';
import { DistrictSummary, RankingEntry } from './types/api';
import { api } from './services/api';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages
import { OverviewPage } from './pages/OverviewPage';
import { MapPage } from './pages/MapPage';
import { RankingsPage } from './pages/RankingsPage';
import { DistrictProfilePage } from './pages/DistrictProfilePage';
import { IndicatorsPage } from './pages/IndicatorsPage';
import { ComparePage } from './pages/ComparePage';
import { ClustersPage } from './pages/ClustersPage';
import { PCAPage } from './pages/PCAPage';
import { ExplainabilityPage } from './pages/ExplainabilityPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { EDAPage } from './pages/EDAPage';
import { MethodologyPage } from './pages/MethodologyPage';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>('overview');
  const [districts, setDistricts] = useState<DistrictSummary[]>([]);
  const [rankings, setRankings] = useState<RankingEntry[]>([]);
  const [selectedDistrictId, setSelectedDistrictId] = useState<string>('KA-005');
  const [apiConnected, setApiConnected] = useState<boolean>(true);
  const [initialLoading, setInitialLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    async function initApp() {
      try {
        const [dList, rList] = await Promise.all([
          api.getDistricts(),
          api.getOverallRankings(),
        ]);
        if (isMounted) {
          setDistricts(dList);
          setRankings(rList);
          setApiConnected(true);
        }
      } catch (err) {
        console.warn('Failed connecting to live backend API, checking health...', err);
        if (isMounted) setApiConnected(false);
      } finally {
        if (isMounted) setInitialLoading(false);
      }
    }
    initApp();
    return () => {
      isMounted = false;
    };
  }, []);

  const pageTitles: Record<PageId, string> = {
    overview: 'Executive Overview Dashboard',
    map: 'Karnataka District Map',
    rankings: 'Karnataka District Rankings',
    district: `District Profile: ${districts.find((d) => d.district_id === selectedDistrictId)?.district_name || selectedDistrictId}`,
    indicators: '14 Indicator Explorer',
    compare: 'Multi-District Comparison Matrix',
    clusters: 'K-Means & Hierarchical Clustering',
    pca: 'Principal Component Analysis (PCA)',
    explainability: 'State-Average Gap Diagnostics',
    recommendations: 'Targeted Policy Recommendations & SDGs',
    eda: 'Exploratory Data Analysis Views',
    methodology: 'Data Methodology & Audit Disclosures',
  };

  const renderContent = () => {
    switch (currentPage) {
      case 'overview':
        return (
          <OverviewPage
            districts={districts}
            rankings={rankings}
            onSelectDistrict={(id) => setSelectedDistrictId(id)}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'map':
        return (
          <MapPage
            rankings={rankings}
            selectedDistrictId={selectedDistrictId}
            onSelectDistrict={(id) => setSelectedDistrictId(id)}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'rankings':
        return (
          <RankingsPage
            onSelectDistrict={(id) => {
              setSelectedDistrictId(id);
              setCurrentPage('district');
            }}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'district':
        return (
          <DistrictProfilePage
            districtId={selectedDistrictId}
            districts={districts}
            onSelectDistrict={(id) => setSelectedDistrictId(id)}
          />
        );
      case 'indicators':
        return <IndicatorsPage />;
      case 'compare':
        return <ComparePage districts={districts} />;
      case 'clusters':
        return (
          <ClustersPage
            onSelectDistrict={(id) => {
              setSelectedDistrictId(id);
              setCurrentPage('district');
            }}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'pca':
        return (
          <PCAPage
            onSelectDistrict={(id) => {
              setSelectedDistrictId(id);
              setCurrentPage('district');
            }}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'explainability':
        return (
          <ExplainabilityPage
            onSelectDistrict={(id) => {
              setSelectedDistrictId(id);
              setCurrentPage('district');
            }}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'recommendations':
        return (
          <RecommendationsPage
            districts={districts}
            selectedDistrictId={selectedDistrictId}
            onSelectDistrict={(id) => setSelectedDistrictId(id)}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
      case 'eda':
        return <EDAPage />;
      case 'methodology':
        return <MethodologyPage />;
      default:
        return (
          <OverviewPage
            districts={districts}
            rankings={rankings}
            onSelectDistrict={(id) => setSelectedDistrictId(id)}
            onNavigatePage={(p) => setCurrentPage(p)}
          />
        );
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-900 text-slate-100">
      {/* Sidebar */}
      <Sidebar currentPage={currentPage} onNavigate={(p) => setCurrentPage(p)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          districts={districts}
          selectedDistrictId={selectedDistrictId}
          onSelectDistrict={(id) => {
            setSelectedDistrictId(id);
            setCurrentPage('district');
          }}
          apiConnected={apiConnected}
          pageTitle={pageTitles[currentPage]}
        />

        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {initialLoading ? (
            <LoadingSpinner message="Initializing InfraSense Analytics Platform..." />
          ) : (
            renderContent()
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
