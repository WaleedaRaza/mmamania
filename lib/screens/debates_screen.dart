import 'package:flutter/material.dart';

class DebatesScreen extends StatefulWidget {
  const DebatesScreen({super.key});

  @override
  _DebatesScreenState createState() => _DebatesScreenState();
}

class _DebatesScreenState extends State<DebatesScreen> with TickerProviderStateMixin {
  int _selectedTab = 0;
  final List<String> _tabs = ['Live Rooms', 'Threads', 'Popular'];
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      body: SafeArea(
          child: Column(
            children: [
              // Header Section
              Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      children: [
                      const Icon(
                          Icons.forum,
                          color: Colors.white,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                      const Text(
                          'Debates',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                  const Text(
                      'Join the MMA Discussion',
                      style: TextStyle(
                      color: Colors.grey,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Tab Selector
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                  borderRadius: BorderRadius.circular(25),
                border: Border.all(color: Colors.grey.withOpacity(0.3)),
                ),
                child: Row(
                  children: _tabs.asMap().entries.map((entry) {
                    int index = entry.key;
                    String tab = entry.value;
                    bool isSelected = _selectedTab == index;
                    
                    return Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedTab = index;
                          });
                        _animationController.reset();
                        _animationController.forward();
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                          color: isSelected ? Colors.red : Colors.transparent,
                            borderRadius: BorderRadius.circular(25),
                          ),
                          child: Text(
                            tab,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                            color: isSelected ? Colors.white : Colors.grey,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              fontSize: 14,
                          ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
              
              const SizedBox(height: 20),
              
            // Content Area
              Expanded(
                    child: FadeTransition(
                      opacity: _fadeAnimation,
                child: _buildTabContent(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent() {
    switch (_selectedTab) {
      case 0:
        return _buildLiveRoomsTab();
      case 1:
        return _buildThreadsTab();
      case 2:
        return _buildPopularTab();
      default:
        return _buildLiveRoomsTab();
    }
  }

  Widget _buildLiveRoomsTab() {
    return Container(
      color: const Color(0xFF0A0A0A),
      child: ListView(
        padding: const EdgeInsets.all(16),
                      children: [
          _buildLiveRoomCard(
            title: "UFC 300 Main Event Discussion",
            participants: 6,
            maxParticipants: 9,
            isLive: true,
            topic: "Pereira vs Hill Analysis",
          ),
          const SizedBox(height: 16),
          _buildLiveRoomCard(
            title: "Who's the GOAT? Silva vs Jones",
            participants: 3,
            maxParticipants: 9,
            isLive: true,
            topic: "Greatest of All Time Debate",
          ),
          const SizedBox(height: 16),
          _buildLiveRoomCard(
            title: "Next UFC Champion Predictions",
            participants: 8,
            maxParticipants: 9,
            isLive: false,
            topic: "Future Champions Discussion",
          ),
          const SizedBox(height: 16),
          _buildLiveRoomCard(
            title: "Best Submission of 2024",
            participants: 2,
            maxParticipants: 9,
            isLive: true,
            topic: "Submission Techniques",
          ),
          const SizedBox(height: 16),
          _buildLiveRoomCard(
            title: "McGregor's Return Speculation",
            participants: 7,
            maxParticipants: 9,
            isLive: true,
            topic: "The Notorious Comeback",
          ),
        ],
      ),
    );
  }

  Widget _buildLiveRoomCard({
    required String title,
    required int participants,
    required int maxParticipants,
    required bool isLive,
    required String topic,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isLive ? Colors.red : Colors.grey.withOpacity(0.3),
          width: isLive ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
                                    ),
                                  ],
                                ),
      child: InkWell(
        onTap: () => _navigateToLiveRoom(title, participants, maxParticipants),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Live indicator
                  if (isLive)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                        color: Colors.red,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.fiber_manual_record, color: Colors.white, size: 12),
                          SizedBox(width: 4),
                          Text(
                                  'LIVE',
                                  style: TextStyle(
                                    color: Colors.white,
                              fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                        
                  const Spacer(),
                  
                  // Join button
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.red),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.add, color: Colors.red, size: 20),
                          onPressed: () => _navigateToLiveRoom(title, participants, maxParticipants),
                          constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                        ),
                        Text(
                          '$participants/$maxParticipants',
                          style: const TextStyle(color: Colors.red, fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(width: 8),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              Text(
                title,
                style: const TextStyle(
                                    color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              const SizedBox(height: 4),
              
              Text(
                topic,
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
              ),
              
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Icon(
                    Icons.people,
                    color: Colors.grey,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '$participants participants',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                  const Spacer(),
                  if (isLive)
                              Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'Join Now',
                        style: TextStyle(color: Colors.red, fontSize: 10, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
              ),
            ],
          ),
                          ),
                        ),
    );
  }

  Widget _buildThreadsTab() {
    return Container(
      color: const Color(0xFF0A0A0A),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildThreadCard(
            title: "UFC 300: Pereira vs Hill Analysis",
            author: "MMA_Analyst",
            replies: 47,
            lastReply: "2 hours ago",
            isHot: true,
          ),
          const SizedBox(height: 12),
          _buildThreadCard(
            title: "Best UFC Comebacks of All Time",
            author: "FightFanatic",
            replies: 23,
            lastReply: "5 hours ago",
            isHot: false,
          ),
          const SizedBox(height: 12),
          _buildThreadCard(
            title: "Who should McGregor fight next?",
            author: "NotoriousFan",
            replies: 89,
            lastReply: "1 hour ago",
            isHot: true,
          ),
          const SizedBox(height: 12),
          _buildThreadCard(
            title: "Technical Breakdown: Khabib's Wrestling",
            author: "GrapplingGuru",
            replies: 34,
            lastReply: "3 hours ago",
            isHot: false,
          ),
          const SizedBox(height: 12),
          _buildThreadCard(
            title: "UFC Rankings Update Discussion",
            author: "RankingsExpert",
            replies: 56,
            lastReply: "4 hours ago",
            isHot: true,
          ),
        ],
      ),
    );
  }

  Widget _buildThreadCard({
    required String title,
    required String author,
    required int replies,
    required String lastReply,
    required bool isHot,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isHot ? Colors.orange.withOpacity(0.5) : Colors.transparent,
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: InkWell(
        onTap: () => _navigateToThread(title),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Avatar placeholder
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.person,
                  color: Colors.red,
                  size: 20,
                ),
              ),
              
              const SizedBox(width: 12),
              
              // Content
          Expanded(
            child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
              children: [
                        Expanded(
                          child: Text(
                            title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (isHot)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.orange.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Text(
                              'HOT',
                              style: TextStyle(color: Colors.orange, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                      ],
                ),
                const SizedBox(height: 4),
                    Text(
                      'by $author',
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.chat_bubble_outline, color: Colors.grey, size: 14),
                        const SizedBox(width: 4),
                        Text(
                          '$replies replies',
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        const SizedBox(width: 16),
                        Icon(Icons.access_time, color: Colors.grey, size: 14),
                    const SizedBox(width: 4),
                    Text(
                          lastReply,
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                      ],
                    ),
                  ],
                ),
                ),
              ],
            ),
          ),
      ),
    );
  }

  Widget _buildPopularTab() {
    return Container(
      color: const Color(0xFF0A0A0A),
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.trending_up, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'Popular Debates',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              'Coming soon...',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToLiveRoom(String title, int participants, int maxParticipants) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LiveRoomScreen(
          title: title,
          participants: participants,
          maxParticipants: maxParticipants,
        ),
      ),
    );
  }

  void _navigateToThread(String title) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ThreadScreen(title: title),
      ),
    );
  }
}

class LiveRoomScreen extends StatefulWidget {
  final String title;
  final int participants;
  final int maxParticipants;

  const LiveRoomScreen({
    Key? key,
    required this.title,
    required this.participants,
    required this.maxParticipants,
  }) : super(key: key);

  @override
  State<LiveRoomScreen> createState() => _LiveRoomScreenState();
}

class _LiveRoomScreenState extends State<LiveRoomScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {'user': 'MMA_Fan1', 'message': 'Pereira is going to dominate!', 'time': '2:30'},
    {'user': 'FightAnalyst', 'message': 'Hill has the reach advantage though', 'time': '2:32'},
    {'user': 'UFC_Expert', 'message': 'This is going to be a war', 'time': '2:35'},
    {'user': 'GrapplingGuru', 'message': 'Ground game will be the key', 'time': '2:37'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        title: Text(
          widget.title,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1A1A1A),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Row(
            mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.fiber_manual_record, color: Colors.white, size: 12),
                SizedBox(width: 4),
                Text(
                  'LIVE',
                  style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          // Participants Grid
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Participants (${widget.participants}/${widget.maxParticipants})',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 1,
                  ),
                  itemCount: widget.maxParticipants,
                  itemBuilder: (context, index) {
                    bool isOccupied = index < widget.participants;
                    return Container(
                      decoration: BoxDecoration(
                        color: isOccupied ? Colors.red.withOpacity(0.2) : const Color(0xFF1A1A1A),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isOccupied ? Colors.red : Colors.grey.withOpacity(0.3),
                          width: 2,
                        ),
                      ),
                      child: isOccupied
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(
                                    Icons.person,
                                    color: Colors.red,
                                    size: 24,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'User ${index + 1}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : Center(
                              child: IconButton(
                                icon: const Icon(Icons.add, color: Colors.grey, size: 24),
                  onPressed: () {
                                  // Join room logic
                ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Joining room...'),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                },
                              ),
                            ),
                    );
                  },
                ),
              ],
            ),
          ),
          
          const Divider(color: Colors.grey, height: 1),
          
          // Chat Section
          Expanded(
            child: Column(
              children: [
                // Messages
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                color: Colors.red.withOpacity(0.2),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.person,
                                color: Colors.red,
                                size: 16,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        message['user'],
                                        style: const TextStyle(
                                          color: Colors.red,
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        message['time'],
                                        style: const TextStyle(
                                          color: Colors.grey,
                                          fontSize: 10,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    message['message'],
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
                
                // Message Input
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: const BoxDecoration(
                    color: Color(0xFF1A1A1A),
                    border: Border(
                      top: BorderSide(color: Colors.grey, width: 0.5),
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            hintText: 'Type your message...',
                            hintStyle: TextStyle(color: Colors.grey),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.all(Radius.circular(25)),
                              borderSide: BorderSide(color: Colors.grey),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.all(Radius.circular(25)),
                              borderSide: BorderSide(color: Colors.grey),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.all(Radius.circular(25)),
                              borderSide: BorderSide(color: Colors.red),
                            ),
                            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          icon: const Icon(Icons.send, color: Colors.white),
                          onPressed: () {
                            if (_messageController.text.isNotEmpty) {
                              setState(() {
                                _messages.add({
                                  'user': 'You',
                                  'message': _messageController.text,
                                  'time': 'now',
                                });
                              });
                              _messageController.clear();
                            }
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ThreadScreen extends StatelessWidget {
  final String title;

  const ThreadScreen({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        title: Text(
          title,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1A1A1A),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.forum, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'Thread Discussion',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              'Coming soon...',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }
} 