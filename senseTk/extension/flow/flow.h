#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <algorithm>
#include <map>
#include <queue>
#define INF 0x3e3e3e3e
#define BIG (INF-2)
#define DEFAULT_THR 400000

using namespace std;

struct Edge
{
	int a, c, f;
	Edge * nxt, * rev;
	Edge(int to, int cost, int flow, Edge * Next) : a(to), c(cost), f(flow), nxt(Next) {
		// a = to;
		// c = cost;
		// nxt = Next;
		rev=NULL;
	}
	Edge() {}
};

struct fhnd
{
	int nodes;
	int thr;
	std::vector<Edge*> * G;
};

typedef Edge E;

std::map<int, fhnd*> flowMap;

int createFlow(int id) {
	if (flowMap.find(id)==flowMap.end()) {
		fhnd * nhnd = new fhnd();
		nhnd->G = new std::vector<Edge*>();
		nhnd->nodes=0;
		nhnd->thr=DEFAULT_THR;
		flowMap[id]=nhnd;
		return 0;
	} else return -1;
}

void freeEdge(Edge * ptr) {
	Edge * pre;
	for (;ptr!=NULL;ptr=pre) {
		pre = ptr->nxt;
		delete ptr;
	}
}

void freeHnd(fhnd * hnd) {
	for (size_t i=0;i<hnd->G->size();++i) freeEdge((*(hnd->G))[i]);
	hnd->G->clear();
	delete hnd->G;
	delete hnd;	
}

void release(int id) {
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		flowMap.erase(id);
		freeHnd(hnd);
	}
}

void clear(int id) {
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		int T = hnd->thr;
		freeHnd(hnd);
		hnd = new fhnd();
		hnd->nodes=0;
		hnd->thr=T;
		hnd->G = new std::vector<Edge*>();
		flowMap[id] = hnd;
	}
}

void setNodes(int id, int cnt1, int cnt2) {
	int cnt=cnt1+cnt2;
	if (flowMap.find(id)!=flowMap.end()) {
		if (cnt<=0) return;
		fhnd * hnd = flowMap[id];
		hnd->nodes=cnt;
		hnd->G->resize(hnd->nodes+2);
		std::vector<Edge*> &G = (*(hnd->G));
		for (size_t i=0;i<hnd->G->size();++i) G[i]=NULL;
		for (int i=1;i<=cnt1;++i) {
			Edge * tmp = new Edge(i,0,1,G[0]);
			G[0] = tmp;
			Edge * rtmp = new Edge(0,0,0,G[i]);
			G[i] = rtmp;
			tmp->rev=rtmp;
			rtmp->rev=tmp;
		}
		for (int i=cnt1+1;i<=cnt1+cnt2;++i) {
			Edge * tmp = new Edge(i,0,0,G[hnd->nodes+1]);
			G[hnd->nodes+1] = tmp;
			Edge * rtmp = new Edge(hnd->nodes+1,0,1,G[i]);
			G[i] = rtmp;
			tmp->rev=rtmp;
			rtmp->rev=tmp;
		}
	}	
}

void setNodes(int id, int cnt1, int cnt_, int cnt2) {
	int cnt=cnt1+cnt2+cnt_;
	if (flowMap.find(id)!=flowMap.end()) {
		if (cnt<=0) return;
		fhnd * hnd = flowMap[id];
		hnd->nodes=cnt;
		hnd->G->resize(hnd->nodes+2);
		std::vector<Edge*> &G = (*(hnd->G));
		for (size_t i=0;i<hnd->G->size();++i) G[i]=NULL;
		// for (int i=1;i<=cnt1;++i) {
		// 	Edge * tmp = new Edge(i,0,1,G[0]);
		// 	G[0] = tmp;
		// 	Edge * rtmp = new Edge(0,INF,1,G[i]);
		// 	G[i] = rtmp;
		// 	tmp->rev=rtmp;
		// 	rtmp->rev=tmp;
		// }
		// for (int i=cnt+1-cnt2;i<=cnt;++i) {
		// 	Edge * tmp = new Edge(i,INF,1,G[hnd->nodes+1]);
		// 	G[hnd->nodes+1] = tmp;
		// 	Edge * rtmp = new Edge(hnd->nodes+1,0,1,G[i]);
		// 	G[i] = rtmp;
		// 	tmp->rev=rtmp;
		// 	rtmp->rev=tmp;
		// }
	}
}

void setThr(int id, int thr) {
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		hnd->thr=thr;
	}	
}

void printParam(int id) {
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		fprintf(stderr,"tracker [%d] has %d(+2) vertex and thr = %d.\n",id,hnd->nodes,hnd->thr);
	} else fprintf(stderr,"tracker [%d] does not exists.\n",id);
}

int addEdge(int id, int a, int b, int c, int f = 1) {
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		std::vector<Edge*> &G=(*(hnd->G));
		int n=hnd->nodes;
		if (a<0||a>n+1||b<0||b>n+1||a==b) return -1;
		Edge * tmp = new Edge(b,c,f,G[a]);
		G[a]=tmp;
		Edge * rtmp = new Edge(a,-c,0,G[b]);
		G[b]=rtmp;
		tmp->rev=rtmp;
		rtmp->rev=tmp;
		return 0;
	}
	else return -1;
}

int spfa(fhnd * hnd, std::vector<int> &mt) {
	int n=hnd->nodes+2;
	std::vector<Edge*> &G=(*(hnd->G));
	queue<int> q;
	std::vector<int> d(n);
	std::vector<bool> inq(n);
	std::vector<int> pre(n);
	std::vector<E*> ped(n);
	for (int i=0;i<n;++i) {
		d[i]=INF;
		inq[i]=false;
	}
	q.push(0);
	inq[0]=true;
	d[0]=0;
	pre[0]=-1;
	ped[0]=NULL;
	while (!q.empty()) {
		int x=q.front();
		q.pop();
		inq[x]=false;
		for (E* p=G[x];p!=NULL;p=p->nxt) {
			int y=p->a, c=p->c;
			if (p->f>0&&c<hnd->thr&&d[x]+c<d[y]) {
				d[y]=d[x]+c;
				pre[y]=x;
				ped[y]=p;
				if (!inq[y]) {
					q.push(y);
					inq[y]=true;
				}
			}
		}
	}
	if (d[n-1]<INF) {
		int nw = n-1;
		while (pre[nw]>=0) {
			// ped[nw]->rev->c = -ped[nw]->c;
			ped[nw]->rev->f += 1;
			ped[nw]->f -= 1;
			// ped[nw]->c = INF;
			if (pre[nw]<nw) mt[pre[nw]]=nw;
			nw=pre[nw];
		}
		return 1;
	}
	return 0;
}

std::vector<int> flow(int id) {
	std::vector<int> res;
	if (flowMap.find(id)!=flowMap.end()) {
		fhnd * hnd = flowMap[id];
		res.resize(hnd->nodes+2,-1);
		while (spfa(hnd, res));
	}
	return res;
}
