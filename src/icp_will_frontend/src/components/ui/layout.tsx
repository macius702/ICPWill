import React from 'react';

interface LayoutProps {
  navItems: React.ReactNode[];
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ navItems, children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md flex flex-col items-center">
        <div className="p-4">
          <h1 className="text-2xl font-semibold text-gray-800">Your App</h1>
        </div>
        <nav className="mt-6">
          {navItems.map((item, idx) => <div key={idx}>{item}</div>)}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;
