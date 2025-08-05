import 'package:supabase_flutter/supabase_flutter.dart';

void main() async {
  // Initialize Supabase
  await Supabase.initialize(
    url: 'YOUR_SUPABASE_URL',
    anonKey: 'YOUR_SUPABASE_ANON_KEY',
  );
  
  final client = Supabase.instance.client;
  
  try {
    print('🔍 Testing rankings query...');
    
    final response = await client
        .from('rankings')
        .select('*, fighters(*)')
        .eq('weight_class', 'Men\'s Pound-for-Pound')
        .order('rank_position', ascending: true);
    
    print('📊 Raw response length: ${response.length}');
    
    if (response.isNotEmpty) {
      print('📊 First ranking: ${response[0]}');
      
      final firstRanking = response[0];
      if (firstRanking['fighters'] != null) {
        print('✅ Fighter data found');
        print('📊 Fighter: ${firstRanking['fighters']}');
      } else {
        print('❌ No fighter data found');
      }
    } else {
      print('❌ No rankings found');
    }
    
  } catch (e) {
    print('❌ Error: $e');
  }
} 