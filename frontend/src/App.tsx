import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppFooter from './components/AppFooter';
import ProtectedRoute from './components/ProtectedRoute';
import SpringFestival from './components/SpringFestival';
import './App.css';
import AuthCallback from './pages/AuthCallback';
import ChapterAnalysis from './pages/ChapterAnalysis';
import ChapterReader from './pages/ChapterReader';
import Chapters from './pages/Chapters';
import Characters from './pages/Characters';
import Careers from './pages/Careers';
import Foreshadows from './pages/Foreshadows';
import Inspiration from './pages/Inspiration';
import Login from './pages/Login';
import MCPPlugins from './pages/MCPPlugins';
import Organizations from './pages/Organizations';
import Outline from './pages/Outline';
import ProjectDetail from './pages/ProjectDetail';
import ProjectList from './pages/ProjectList';
import ProjectWizardNew from './pages/ProjectWizardNew';
import PromptTemplates from './pages/PromptTemplates';
import PromptWorkshop from './pages/PromptWorkshop';
import RelationshipGraph from './pages/RelationshipGraph';
import Relationships from './pages/Relationships';
import Settings from './pages/Settings';
import Sponsor from './pages/Sponsor';
import UserManagement from './pages/UserManagement';
import WorldSetting from './pages/WorldSetting';
import WritingStyles from './pages/WritingStyles';

function App() {
  return (
    <>
      <SpringFestival />
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route path="/login" element={<><Login /><AppFooter /></>} />
          <Route path="/auth/callback" element={<AuthCallback />} />

          <Route path="/" element={<ProtectedRoute><><ProjectList /><AppFooter sidebarWidth={220} /></></ProtectedRoute>} />
          <Route path="/projects" element={<ProtectedRoute><><ProjectList /><AppFooter sidebarWidth={220} /></></ProtectedRoute>} />
          <Route path="/wizard" element={<ProtectedRoute><ProjectWizardNew /></ProtectedRoute>} />
          <Route path="/inspiration" element={<ProtectedRoute><Inspiration /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="/prompt-templates" element={<ProtectedRoute><><PromptTemplates /><AppFooter /></></ProtectedRoute>} />
          <Route path="/mcp-plugins" element={<ProtectedRoute><MCPPlugins /></ProtectedRoute>} />
          <Route path="/user-management" element={<ProtectedRoute><UserManagement /></ProtectedRoute>} />
          <Route path="/chapters/:chapterId/reader" element={<ProtectedRoute><ChapterReader /></ProtectedRoute>} />
          <Route path="/project/:projectId" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>}>
            <Route index element={<Navigate to="sponsor" replace />} />
            <Route path="world-setting" element={<WorldSetting />} />
            <Route path="careers" element={<Careers />} />
            <Route path="outline" element={<Outline />} />
            <Route path="characters" element={<Characters />} />
            <Route path="relationships" element={<Relationships />} />
            <Route path="relationships-graph" element={<RelationshipGraph />} />
            <Route path="organizations" element={<Organizations />} />
            <Route path="chapters" element={<Chapters />} />
            <Route path="chapter-analysis" element={<ChapterAnalysis />} />
            <Route path="foreshadows" element={<Foreshadows />} />
            <Route path="writing-styles" element={<WritingStyles />} />
            <Route path="prompt-workshop" element={<PromptWorkshop />} />
            <Route path="sponsor" element={<Sponsor />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
