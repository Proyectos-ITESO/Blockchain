/**
 * Main chat page with split layout
 */

import { useAuth } from '../contexts/AuthContext';
import { ChatProvider } from '../contexts/ChatContext';
import ContactList from '../components/ContactList';
import MessageWindow from '../components/MessageWindow';
import UserSettings from '../components/UserSettings';

function ChatLayout() {
  return (
    <div className="h-screen flex overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 flex-shrink-0 h-full overflow-hidden">
        <ContactList />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <MessageWindow />
      </div>

      {/* Settings panel */}
      <UserSettings />
    </div>
  );
}

export default function Chat() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <ChatProvider>
      <ChatLayout />
    </ChatProvider>
  );
}
