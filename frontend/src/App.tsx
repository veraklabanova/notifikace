import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import CalendarPage from './pages/CalendarPage';
import Notifications from './pages/Notifications';
import Rules from './pages/Rules';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/rules" element={<Rules />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
