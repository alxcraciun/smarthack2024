import { useEffect, useState } from "react";
import { 
    Card,
    CardHeader,
    Title,
} from '@ui5/webcomponents-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const HomePage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8082')
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="flex h-screen items-center justify-center">
      <p className="text-xl">Loading data...</p>
    </div>;
  }

  if (error) {
    return <div className="flex h-screen items-center justify-center">
      <p className="text-xl text-red-500">Error: {error}</p>
    </div>;
  }

  return (
    <div className="p-8">
      <Title className="text-4xl font-bold mb-8">Smarthack 2024 Dashboard</Title>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <Title>Daily Migrations</Title>
          </CardHeader>
          <div className="h-96 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="migrations_count" 
                  stroke="#8884d8" 
                  name="Migrations"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <Title>Daily Demands</Title>
          </CardHeader>
          <div className="h-96 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="demands_count" 
                  stroke="#82ca9d" 
                  name="Demands"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <Title>Daily Cost and CO2</Title>
          </CardHeader>
          <div className="h-96 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="daily_cost" 
                  stroke="#ff7300" 
                  name="Cost"
                />
                <Line 
                  type="monotone" 
                  dataKey="daily_co2" 
                  stroke="#387908" 
                  name="CO2"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <Title>Total Cost and CO2</Title>
          </CardHeader>
          <div className="h-96 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="total_cost" 
                  stroke="#ff7300" 
                  name="Total Cost"
                />
                <Line 
                  type="monotone" 
                  dataKey="total_co2" 
                  stroke="#387908" 
                  name="Total CO2"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default HomePage;