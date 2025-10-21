import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { MemoryGallery } from './src/components/MemoryGallery';
import { sampleMemories } from './src/data/sampleMemories';

export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <MemoryGallery memories={sampleMemories} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
});
