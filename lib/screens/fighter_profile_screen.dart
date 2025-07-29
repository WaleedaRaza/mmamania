import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/fighter.dart';
import '../services/ufc_data_service.dart';
import '../services/ufc_url_service.dart';

class FighterProfileScreen extends StatefulWidget {
  final String fighterId;

  const FighterProfileScreen({Key? key, required this.fighterId}) : super(key: key);

  @override
  State<FighterProfileScreen> createState() => _FighterProfileScreenState();
}

class _FighterProfileScreenState extends State<FighterProfileScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  Fighter? fighter;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadFighterData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadFighterData() async {
    setState(() {
      isLoading = true;
    });

    try {
      final ufcService = UFCDataService();
      await ufcService.loadData();
      
      // Try to find fighter by ID first, then by name
      Fighter? foundFighter = ufcService.getFighterById(widget.fighterId);
      
      // If fighter found but division is empty, try to get division from rankings
      if (foundFighter != null && (foundFighter.division.isEmpty || foundFighter.division == 'Unknown')) {
        // Look for the fighter in rankings to get division
        if (foundFighter != null) {
          for (String division in ufcService.getDivisions()) {
            final rankings = ufcService.getRankingsForDivision(division);
            for (var ranking in rankings) {
              if (ranking.fighterId == widget.fighterId || 
                  ranking.fighterName.toLowerCase() == foundFighter!.name.toLowerCase()) {
                // Create updated fighter with division from ranking
                foundFighter = Fighter(
                  id: foundFighter!.id,
                  name: foundFighter!.name,
                  division: ranking.division, // Use division from ranking
                  record: foundFighter!.record,
                  imageUrl: foundFighter!.imageUrl,
                  status: foundFighter!.status,
                  placeOfBirth: foundFighter!.placeOfBirth,
                  trainingAt: foundFighter!.trainingAt,
                  fightingStyle: foundFighter!.fightingStyle,
                  age: foundFighter!.age,
                  height: foundFighter!.height,
                  weight: foundFighter!.weight,
                  octagonDebut: foundFighter!.octagonDebut,
                  reach: foundFighter!.reach,
                  legReach: foundFighter!.legReach,
                  stats: foundFighter!.stats,
                  fightHistory: foundFighter!.fightHistory,
                );
                break;
              }
            }
            if (foundFighter!.division != 'Unknown' && foundFighter!.division.isNotEmpty) {
              break;
            }
          }
        }
      }
      
      setState(() {
        fighter = foundFighter;
        isLoading = false;
      });
    } catch (e) {
      print('Error loading fighter data: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF1A1A1A),
      appBar: AppBar(
        title: Text(
          fighter?.name ?? 'Fighter Profile',
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: Color(0xFF2D2D2D),
        iconTheme: const IconThemeData(color: Colors.white),
        elevation: 0,
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(
                color: Colors.red,
              ),
            )
          : fighter == null
              ? _buildNotFound()
              : _buildFighterProfile(),
    );
  }

  Widget _buildNotFound() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.person_off,
            size: 64,
            color: Colors.grey[600],
          ),
          const SizedBox(height: 16),
          Text(
            'Fighter not found',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ID: ${widget.fighterId}',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFighterProfile() {
    return Column(
      children: [
        // Header with fighter info
        _buildHeader(),
        
        // Tab bar
        Container(
          color: Color(0xFF2D2D2D),
          child: TabBar(
            controller: _tabController,
            indicatorColor: Colors.red,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.grey,
            tabs: const [
              Tab(text: 'Overview'),
              Tab(text: 'Info'),
            ],
          ),
        ),
        
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildOverviewTab(),
              _buildInfoTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF2D2D2D), Color(0xFF1A1A1A)],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        children: [
          // Fighter image placeholder
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.grey[700],
              borderRadius: BorderRadius.circular(60),
            ),
            child: const Icon(
              Icons.person,
              size: 60,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          
          // Fighter name
          Text(
            fighter!.name,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          
          // Division
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              fighter!.division.isNotEmpty ? fighter!.division : 'Unknown Division',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          
          // Record
          Text(
            '${fighter!.record.wins}-${fighter!.record.losses}-${fighter!.record.draws}',
            style: const TextStyle(
              fontSize: 18,
              color: Colors.white70,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 16),
          
          // UFC Stats Button
          _buildUFCStatsButton(),
        ],
      ),
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildInfoCard(
            'Record',
            '${fighter!.record.wins} Wins • ${fighter!.record.losses} Losses • ${fighter!.record.draws} Draws',
            Icons.sports_martial_arts,
          ),
          const SizedBox(height: 16),
          
          if (fighter!.fightingStyle != null)
            _buildInfoCard(
              'Fighting Style',
              fighter!.fightingStyle!,
              Icons.fitness_center,
            ),
          
          if (fighter!.fightingStyle != null) const SizedBox(height: 16),
          
          if (fighter!.status != null)
            _buildInfoCard(
              'Status',
              fighter!.status!,
              Icons.info,
            ),
          
          if (fighter!.status != null) const SizedBox(height: 16),
          
          _buildInfoCard(
            'Division',
            fighter!.division.isNotEmpty ? fighter!.division : 'Unknown Division',
            Icons.category,
          ),
        ],
      ),
    );
  }

  Widget _buildStatsTab() {
    final stats = fighter!.stats;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Fight Statistics',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          
          _buildStatCard('Fight Win Streak', '${stats.fightWinStreak}', Icons.trending_up),
          _buildStatCard('Wins by KO/TKO', '${stats.winsByKnockout}', Icons.sports_martial_arts),
          _buildStatCard('Wins by Submission', '${stats.winsBySubmission}', Icons.sports_martial_arts),
          _buildStatCard('Striking Accuracy', '${stats.strikingAccuracy.toStringAsFixed(1)}%', Icons.gps_fixed),
          _buildStatCard('Takedown Accuracy', '${stats.takedownAccuracy.toStringAsFixed(1)}%', Icons.download),
          _buildStatCard('Strikes Landed/Min', '${stats.sigStrikesLandedPerMin.toStringAsFixed(2)}', Icons.speed),
          _buildStatCard('Strikes Absorbed/Min', '${stats.sigStrikesAbsorbedPerMin.toStringAsFixed(2)}', Icons.shield),
          _buildStatCard('Takedowns/15min', '${stats.takedownAvgPer15Min.toStringAsFixed(2)}', Icons.download),
          _buildStatCard('Submissions/15min', '${stats.submissionAvgPer15Min.toStringAsFixed(2)}', Icons.sports_martial_arts),
          _buildStatCard('Striking Defense', '${stats.sigStrikesDefense.toStringAsFixed(1)}%', Icons.shield),
          _buildStatCard('Takedown Defense', '${stats.takedownDefense.toStringAsFixed(1)}%', Icons.block),
          _buildStatCard('Knockdowns/15min', '${stats.knockdownAvg.toStringAsFixed(2)}', Icons.sports_martial_arts),
          _buildStatCard('Average Fight Time', stats.averageFightTime, Icons.timer),
        ],
      ),
    );
  }

  Widget _buildFightsTab() {
    final fights = fighter!.fightHistory;
    
    if (fights.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: Colors.grey[600],
            ),
            const SizedBox(height: 16),
            Text(
              'No fight history available',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: fights.length,
      itemBuilder: (context, index) {
        final fight = fights[index];
        return _buildFightCard(fight);
      },
    );
  }

  Widget _buildInfoTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (fighter!.age != null)
            _buildInfoCard('Age', '${fighter!.age} years old', Icons.person),
          
          if (fighter!.age != null) const SizedBox(height: 16),
          
          if (fighter!.height != null)
            _buildInfoCard('Height', '${fighter!.height}"', Icons.height),
          
          if (fighter!.height != null) const SizedBox(height: 16),
          
          if (fighter!.weight != null)
            _buildInfoCard('Weight', '${fighter!.weight} lbs', Icons.monitor_weight),
          
          if (fighter!.weight != null) const SizedBox(height: 16),
          
          if (fighter!.reach != null)
            _buildInfoCard('Reach', '${fighter!.reach}"', Icons.straighten),
          
          if (fighter!.reach != null) const SizedBox(height: 16),
          
          if (fighter!.legReach != null)
            _buildInfoCard('Leg Reach', '${fighter!.legReach}"', Icons.straighten),
          
          if (fighter!.legReach != null) const SizedBox(height: 16),
          
          if (fighter!.placeOfBirth != null)
            _buildInfoCard('Birthplace', fighter!.placeOfBirth!, Icons.location_on),
          
          if (fighter!.placeOfBirth != null) const SizedBox(height: 16),
          
          if (fighter!.trainingAt != null)
            _buildInfoCard('Training At', fighter!.trainingAt!, Icons.fitness_center),
          
          if (fighter!.trainingAt != null) const SizedBox(height: 16),
          
          if (fighter!.octagonDebut != null)
            _buildInfoCard('Octagon Debut', fighter!.octagonDebut!, Icons.event),
        ],
      ),
    );
  }

  Widget _buildInfoCard(String title, String value, IconData icon) {
    return Card(
      color: Color(0xFF2D2D2D),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              icon,
              color: Colors.red,
              size: 24,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Card(
      color: Color(0xFF2D2D2D),
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              icon,
              color: Colors.red,
              size: 24,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                ),
              ),
            ),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFightCard(FightResult fight) {
    Color resultColor;
    IconData resultIcon;
    
    switch (fight.result.toLowerCase()) {
      case 'win':
        resultColor = Colors.green;
        resultIcon = Icons.check_circle;
        break;
      case 'loss':
        resultColor = Colors.red;
        resultIcon = Icons.cancel;
        break;
      case 'draw':
        resultColor = Colors.orange;
        resultIcon = Icons.remove_circle;
        break;
      default:
        resultColor = Colors.grey;
        resultIcon = Icons.help;
    }
    
    return Card(
      color: Color(0xFF2D2D2D),
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              resultIcon,
              color: resultColor,
              size: 24,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    fight.opponent,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${fight.result} by ${fight.method}',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 14,
                    ),
                  ),
                  if (fight.round != null)
                    Text(
                      'Round ${fight.round}',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 12,
                      ),
                    ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  fight.result.toUpperCase(),
                  style: TextStyle(
                    color: resultColor,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (fight.event != null)
                  Text(
                    fight.event!,
                    style: TextStyle(
                      color: Colors.grey[500],
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.right,
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUFCStatsButton() {
    return Container(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () async {
          try {
            final url = UFCUrlService.generateFighterStatsUrl(fighter!.name);
            final uri = Uri.parse(url);
            
            if (await canLaunchUrl(uri)) {
              await launchUrl(uri, mode: LaunchMode.externalApplication);
            } else {
              // Show error message if URL can't be launched
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Could not open UFC stats page'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          } catch (e) {
            // Show error message if there's an exception
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error opening UFC stats: $e'),
                backgroundColor: Colors.red,
              ),
            );
          }
        },
        icon: const Icon(Icons.open_in_new, color: Colors.white),
        label: const Text(
          'View UFC Stats & Records',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }
} 